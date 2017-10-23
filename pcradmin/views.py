from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from registrations.models import *
from events.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from functools import reduce
from registrations.urls import *
from registrations.views import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from oasis2017.settings import BASE_DIR
import sendgrid
import os
from sendgrid.helpers.mail import *
import xlsxwriter
from time import gmtime, strftime
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
from oasis2017.keyconfig import *
import string
from random import choice
chars = string.letters + string.digits

from django.contrib import messages
from django.db.models import Q

def get_event_string(participant):
    participation_set = Participation.objects.filter(participant=participant, pcr_approved=True)
    events = ''
    for participation in participation_set:
        events += participation.event.name + ', '
    events = events[:-2]
    return events

@staff_member_required
def index(request):
	return redirect('pcradmin:college')

@staff_member_required
def college(request):
	rows = [{'data':[college.name,college.participant_set.filter(pcr_approved=True).count(),college.participant_set.filter(email_verified=True).count()],'link':[{'title':'Manage CR', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})},{'title':'Approve Participations', 'url':reverse('pcradmin:approve_participations', kwargs={'id':college.id})}] } for college in College.objects.all()]
	tables = [{'title':'List of Colleges', 'rows':rows, 'headings':['College', 'Confirmed','Total Participants', 'Manage Cr', 'Approve Participations']}]
	return render(request, 'pcradmin/tables.html', {'tables':tables})

@staff_member_required
def select_college_rep(request, id):
	college = get_object_or_404(College, id=id)
	if request.method == 'POST':
		data = request.POST
		try:
			part_id = data['data']
		except:
			messages.warning(request,'Select a Participant')
			return redirect(request.META.get('HTTP_REFERER'))
		if 'delete' == data['submit']:
			part = Participant.objects.get(id=part_id)
			user = part.user
			user.delete()
			part.user = None
			part.is_cr=False
			part.cr_approved=False
			part.save()
		elif 'select' == data['submit']:
			try:
				Participant.objects.get(college=college,is_cr=True)
				messages.warning(request,'College Representative already selected.')
				return redirect(request.META.get('HTTP_REFERER'))			
			except:
				pass
			part = Participant.objects.get(id=part_id)
			part.is_cr=True
			part.cr_approved=True

			encoded = gen_barcode(part)
			part.save()
			user = part.user
			if not user == None:
				messages.warning(request,'College Representative already selected.')
				return redirect(request.META.get('HTTP_REFERER'))
			if user == None:
				username = part.name.split(' ')[0] + str(part_id)
				length = 8
				password = ''.join(choice(chars) for _ in xrange(length)) 
				user = User.objects.create(username=username, password='')
				user.set_password(password)
				user.save()
				part.user = user
				part.save()
			body = """<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
			<center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 47th edition of OASIS, the annual cultural fest of Birla Institute of Technology & Science, Pilani, India. This year, OASIS will be held from October 31st to November 4th.             
           
This is to inform you that you have been selected as the College Representative for your college.
You can now login <a href="%s">here</a> using the following credentials:
username : '%s'
password : '%s'
We would be really happy to see your college represented at our fest.
It is your responsibility to confirm the participants for different events.

Please make sure to upload your <b>Picture</b> as well as <b>verification documents(Preferably Bonafide Certificate for as many participants as possible)</b> once you login to complete your registration.

We look forward to seeing you at OASIS 2017.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT OASIS 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
StuCCAn (Head)
Dept. of Publications & Correspondence, OASIS 2017
BITS Pilani
%s
pcr@bits-oasis.org
</pre>
			""" %(part.name,str(request.build_absolute_uri(reverse('registrations:home'))),username, password, get_pcr_number())
			subject = 'College Representative for Oasis'
			from_email = Email('register@bits-oasis.org')
			to_email = Email(part.email)
			content = Content('text/html', body)
			sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
			try:
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())
				messages.warning(request,'Email sent to ' + part.name)
			except :
				part.user = None
				part.is_cr = False
				user.delete()
				part.save()
				messages.warning(request,'Email not sent. Please select College Representative again.')
			return redirect(request.META.get('HTTP_REFERER'))


	participants = college.participant_set.filter(email_verified=True)
	try:
		cr = Participant.objects.get(college=college, is_cr=True)
		participants = participants.exclude(id=cr.id)
	except:
		cr=[]
	parts = [{'data':[part.name, part.phone, part.email, part.gender, part.pcr_approved, part.head_of_society, part.year_of_study, event_list(part),is_profile_complete(part), how_much_paid(part)], "id":part.id,} for part in participants]
	print parts
	return render(request, 'pcradmin/college_rep.html',{'college':college, 'parts':parts, 'cr':cr})

def event_list(part):
	events = ''
	for participation in Participation.objects.filter(participant = part):
		events += participation.event.name + ', '
	
	events = events[:-2]
	return events

@staff_member_required
def approve_participations(request, id):
	college = College.objects.get(id=id)
	try:
		cr = Participant.objects.get(college=college, is_cr=True)
	except:
		messages.warning(request, 'CR not selected yet. Please select a College Rep. first for '+college.name)
		return redirect(request.META.get('HTTP_REFERER'))
	if request.method == 'POST':
		data = request.POST
		try:
			part_list = data.getlist('data')
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		if data['submit'] == 'approve':
			for participation in Participation.objects.filter(id__in=part_list):
				participation.pcr_approved = True
				participant = participation.participant	
				participant.pcr_approved = True
				participant.save()
				participation.save()
			message = "Profiles Verified"
		elif data['submit'] == 'disapprove':
			for participation in Participation.objects.filter(id__in=part_list):
				participation.pcr_approved = False
				participation.save()
				participant = participation.participant	
				x = [not p.pcr_approved for p in Participation.objects.filter(participant=participant)]
				if all(x):
					participant.pcr_approved=False
					participant.save()
			message = 'Events successfully unconfirmed'
		messages.success(request, message)
	approved = Participation.objects.filter(participant__college=college, pcr_approved=True, cr_approved=True)
	disapproved = Participation.objects.filter(participant__college=college, pcr_approved=False, cr_approved=True)
	return render(request, 'pcradmin/approve_participations.html', {'approved':approved, 'disapproved':disapproved, 'cr':cr})

@staff_member_required
def verify_profile(request, part_id):
	part = Participant.objects.get(id=part_id)

	if request.method=='POST':
		try:
			data = dict(request.POST)['data']
		except:
			messages.success(request, 'Please select atleast one Event')
			return redirect(request.META.get('HTTP_REFERER'))
		if request.POST['submit'] == 'confirm':
			Participation.objects.filter(id__in=data, cr_approved=True).update(pcr_approved=True)
			part.pcr_approved = True
			message = part.name + '\'s Profile Verified'
		elif request.POST['submit'] == 'unconfirm':
			Participation.objects.filter(id__in=data, cr_approved=True).update(pcr_approved=False)
			message = 'Events successfully unconfirmed'
			x = [not p.pcr_approved for p in Participation.objects.filter(participant=part)]
			if all(x):
				part.pcr_approved=False
				message += ' and ' + part.name + '\'sprofile is uncofirmed'
		part.save()
		messages.success(request, message)
		return redirect(reverse('pcradmin:select_college_rep', kwargs={'id':part.college.id}))
	try:
		profile_url = part.profile_pic.url
		docs_url = part.verify_docs.url
	except:
		message = part.name + '\'s Profile not complete yet.'
		messages.warning(request, message)
		return redirect(request.META.get('HTTP_REFERER'))

	participations = part.participation_set.all()
	events_confirmed = [{'event':p.event, 'id':p.id} for p in participations.filter(pcr_approved=True)]
	events_unconfirmed = [{'event':p.event, 'id':p.id} for p in participations.filter(pcr_approved=False)]
	return render(request, 'pcradmin/verify_profile.html',
	{'profile_url':profile_url, 'docs_url':docs_url, 'part':part, 'confirmed':events_confirmed, 'unconfirmed':events_unconfirmed})

################################ STATS ########################################3

@staff_member_required
def stats(request, order=None):
	if order==None:
		order = 'collegewise'
	if order=='collegewise':
		rows = []
		for college in College.objects.all():
			parts = college.participant_set.all()
			try:
				p=parts.filter(is_cr=True)[0]
				cr = 'True (' + p.name + ')'
			except:
				cr = False

			parts_m = parts.filter(gender='M')
			parts_f = parts.filter(gender='F')
			rows.append({'data':[college.name, cr,participants_count(parts_m), participants_count(parts_f), participants_count(parts), profile_stats(parts)], 'link':[]})
		parts = Participant.objects.all()
		rows.append({'data':['Total', ' ',participants_count(parts.filter(gender='M')), participants_count(parts.filter(gender='F')), participants_count(parts), ' - - '], 'link':[]})
		headings = ['College', 'CR Selected', 'Male', 'Female','Stats', 'Profile status']
		title = 'CollegeWise Participants Stats'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})


	if order == 'eventwise':
		rows = []
		for event in Event.objects.all():
			participations = Participation.objects.filter(event=event)
			if participations.count()>0:
				parts = Participant.objects.filter(id__in=[p.participant.id for p in participations])
				parts_m = parts.filter(gender='M')
				parts_f = parts.filter(gender='F')
				rows.append({'data':[event.name, event.category, participants_count(parts_m), 
					participants_count(parts_f), participants_count(parts)], 'link':[{'title':'View','url':reverse('pcradmin:stats_event', kwargs={'e_id':event.id})}]})
		# parts = Participant.objects.filter(id__in=[p.id for p in Participant.objects.all() if p.participation_set.all().count()>0])
		# parts_m  = parts.filter(gender='M')
		# parts_f = parts.filter(gender='F')
		# rows.append({'data':['Total', ' ', participants_count(parts_m), participants_count(parts_f), participants_count(parts)], 'link':[{'url':'#', 'title':'- - -'}]})
		headings = ['Event', 'Category', 'Male', 'Female', 'Total', 'View']
		title = 'Eventwise Participants Stats'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})
	if order == 'paidwise':
		rows = [{'data':[part.name, part.college.name, part.gender, part.phone, part.email, get_payment_status(part), get_event_string(part)], 'link':[]} for part in Participant.objects.filter(Q(pcr_approved=True), Q(paid=True)|Q(curr_paid=True))]
		headings = ['Name', 'College', 'Gender', 'Phone', 'Email', 'Payment made', 'Events']
		title = 'Participants\' payment status'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})

def get_payment_status(part):
	if part.paid or part.curr_paid:
		if part.controlz_paid or part.curr_controlz_paid:
			return 950
		else:
			return 300
	else:
		return 0

@staff_member_required
def stats_event(request, e_id):
	event = get_object_or_404(Event, id=e_id)
	rows = []
	for college in College.objects.all():
		parts1 = college.participant_set.filter(email_verified=True)
		parts = Participant.objects.filter(id__in=[p.id for p in parts1 if Participation.objects.filter(participant=p, event=event)])
		if not parts:
			continue
		try:
			p=parts.filter(is_cr=True)[0]
			cr = 'True (' + p.name + ')'
		except:
			cr = False

		parts_m = parts.filter(gender='M')
		parts_f = parts.filter(gender='F')
		rows.append({'data':[college.name, cr,participants_count(parts_m), participants_count(parts_f), participants_count(parts), profile_stats(parts)], 'link':[{'url':request.build_absolute_uri(reverse('pcradmin:stats_event_college', kwargs={'e_id':event.id, 'c_id':college.id})), 'title':'View Participants'}]})
	parts = Participant.objects.filter(id__in=[p.id for p in Participant.objects.filter(email_verified=True) if Participation.objects.filter(participant=p, event=event)])
	rows.append({'data':['Total', ' ',participants_count(parts.filter(gender='M')), participants_count(parts.filter(gender='F')), participants_count(parts), ' - - '], 'link':[{'':''}]})
	headings = ['College', 'CR Selected', 'Male', 'Female','Stats', 'Profile status', 'View Details']
	title = 'CollegeWise Participants Stats for ' + event.name
	return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})

@staff_member_required
def stats_event_college(request, e_id, c_id):
	event = get_object_or_404(Event, id=e_id)
	college = get_object_or_404(College, id=c_id)
	parts1 = college.participant_set.filter(email_verified=True)
	parts = Participant.objects.filter(id__in=[p.id for p in parts1 if Participation.objects.filter(participant=p, event=event)])
	rows = [{'data':[part.name, part.college.name, get_cr_name(part),part.gender, part.phone, part.email, Participation.objects.get(participant=part, event=event).pcr_approved, part.paid or part.curr_paid], 'link':[]} for part in parts]
	headings = ['Name', 'College', 'CR', 'Gender', 'Phone', 'Email', 'PCr Approval', 'Payment Status']
	title = 'Participants\' Stats for ' + event.name + ' from ' + college.name
	return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})

def get_cr_name(part):
	return Participant.objects.get(college=part.college, is_cr=True).name

@staff_member_required
def master_stats(request):

	if request.method == 'POST':
		data = request.POST
		print data
		try:
			colleges = data.getlist('college')
		except:
			pass
		try:
			events = data.getlist('event')
		except:
			pass
		if not colleges and not events:
			return redirect(request.META.get('HTTP_REFERRER'))
		print colleges, events[0]
		if colleges[0]!='' and events[0]!='':
			parts = []
			for college_name in colleges:
				try:
					college = College.objects.get(name=college_name)
				except:
					continue
				for event_name in events:
					try:
						event = Event.objects.get(name=event_name)
					except:
						continue
					participations = Participation.objects.filter(event=event)
					parts += Participant.objects.filter(id__in=[p.participant.id for p in participations], college=college)
			rows = [{'data':[part.name, part.college.name, part.gender, part.phone, part.email, part.pcr_approved, part.paid or part.curr_paid], 'link':[]} for part in parts]
			headings = ['Name', 'College', 'Gender', 'Phone', 'Email', 'PCr Approval', 'Payment Status']
			event_names = ''
			for event_name in events:
				event_names += event_name + ', '
			event_names = event_names[:-2]
			college_names = ''
			for college_name in colleges:
				college_names += college_name + ', '
			college_names = college_names[:-2]
			title = 'Participants\' registered for %s event from %s college.' %(event_names, college_names)

		elif events[0]!='':
			parts = []
			for event_name in events:
				try:
					participations = Participation.objects.filter(event=Event.objects.get(name=event_name))
				except:
					continue
				parts += Participant.objects.filter(id__in=[p.participant.id for p in participations])
			rows = [{'data':[part.name, part.college.name, part.gender, part.phone, part.email, part.pcr_approved, part.paid or part.curr_paid], 'link':[]} for part in parts]
			headings = ['Name', 'College', 'Gender', 'Phone', 'Email', 'PCr Approval', 'Payment Status']
			title = 'Participants\' registered for %s event.' %(event_name)
			# return render(request, 'pcradmin/master_stats.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})

		else:
			parts = []
			for college_name in colleges:
				try:
					college = College.objects.get(name=college_name)
				except:
					continue
				parts += college.participant_set.all()
			rows = [{'data':[part.name, part.college.name, part.gender, part.phone, part.email, part.pcr_approved, part.paid or part.curr_paid], 'link':[]} for part in parts]
			headings = ['Name', 'College', 'Gender', 'Phone', 'Email', 'PCr Approval', 'Payment Status']
			title = 'Participants\' registered from %s college.' %(college_name)
		table = {
			'rows':rows,
			'headings':headings,
			'title':title,
			}
		events = Event.objects.all()
		colleges = College.objects.all()		
		return render(request, 'pcradmin/master_stats.html', {'tables':[table, ], 'colleges':colleges, 'events':events})
	events = Event.objects.all()
	colleges = College.objects.all()		
	return render(request, 'pcradmin/master_stats.html', { 'colleges':colleges, 'events':events})

@staff_member_required
def add_college(request):
	if request.method == 'POST':
		data = request.POST
		if data['submit'] == 'add':
			try:
				name = request.POST['name']
				if name=='':
					raise Exception
			except:
				messages.warning(request, 'Please Don\'t leave the name field empty')
				return redirect(request.META.get('HTTP_REFERER'))
			College.objects.create(name=name)
			messages.warning(request, 'College succesfully added')
			return redirect('pcradmin:add_college')
		
		elif data['submit'] == 'delete':
				college = College.objects.get(id=data['data'])
				college.delete()
				messages.warning(request, 'College succesfully deleted')
				return redirect('pcradmin:add_college')
	rows = [{'data':[college.name, college.participant_set.all().count(),  college.participant_set.filter(pcr_approved=True).count()], 'id':college.id, 'link':[{'title':'Select College Representative', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})}]} for college in College.objects.all()]
	headings = ['Name', 'Registered Participants' , 'PCr approved Participants', 'Select/Modify CR']
	title = "College List"
	table = {
		'rows':rows,
		'headings':headings,
		'title':title,
	}
	return render(request, 'pcradmin/add_college.html', {'table':table})

@staff_member_required
def view_final(request):
	rows = [{'data':[college.name,college.participant_set.filter(pcr_approved=True, pcr_final=True).count(),college.participant_set.filter(pcr_approved=True).count()],'link':[{'title':'Select', 'url':reverse('pcradmin:final_confirmation', kwargs={'c_id':college.id})}] } for college in College.objects.all()]
	tables = [{'title':'List of Colleges', 'rows':rows, 'headings':['College', 'Finalised','Total Approved', 'Select']}]
	return render(request, 'pcradmin/tables.html', {'tables':tables})


@staff_member_required
def final_confirmation(request, c_id):
	college = College.objects.get(id=c_id)
	if request.method == 'POST':
		data = request.POST
		try:
			id_list = data.getlist('data')
		except:
			messages.warning(request,'Select a Participant')
			return redirect(request.META.get('HTTP_REFERER'))
		if not id_list:
			messages.warning(request,'Select a Participant')
			return redirect(request.META.get('HTTP_REFERER'))
		parts = Participant.objects.filter(id__in=id_list)
		if data['action'] == 'approve':
			emailgroup = EmailGroup.objects.create()
			for part in parts:
				part.email_group = emailgroup
				part.save()
			return redirect(reverse('pcradmin:final_email', kwargs = {'eg_id':emailgroup.id}))
		elif data['action'] == 'disapprove':
			for part in parts:
				part.email_group = None
				part.pcr_final = False
				part.save()
	parts = college.participant_set.filter(pcr_approved=True, pcr_final=False)
	parts_final = college.participant_set.filter(pcr_approved=True,pcr_final=True)
	return render(request, 'pcradmin/final_confirmation.html', {'parts':parts, 'college':college, 'parts_final':parts_final})

@staff_member_required
def final_email(request, eg_id):
	email_group = EmailGroup.objects.get(id=eg_id)
	parts = email_group.participant_set.all()
	college = parts[0].college
	return render(request, 'pcradmin/final_mail.html', {'parts':parts, 'group':email_group, 'college':college})

@staff_member_required
def final_email_send(request, eg_id):
	email_group = EmailGroup.objects.get(id=eg_id)
	parts = email_group.participant_set.all()
	college = parts[0].college
	try:
		_dir = '/root/live/oasis/backend/resources/oasis2017/'
		doc_name = _dir + 'final_list.pdf'
		a=create_final_pdf(eg_id, doc_name, _dir)
	except:
		_dir = '/home/auto-reload/Downloads/'
		doc_name = _dir + 'final_list.pdf'
		a=create_final_pdf(eg_id, doc_name, _dir)
	import base64

	with open(a, "rb") as output_pdf:
		encoded_string1 = base64.b64encode(output_pdf.read())
	attachment = Attachment()
	attachment.content = encoded_string1
	attachment.filename = 'Confirmed_Participants.pdf'
	with open(_dir+'Instructions_to_Participants', 'rb') as output_doc:
		encoded_string2 = base64.b64encode(output_doc.read())
	attachment_1 = Attachment()
	attachment_1.content = encoded_string2
	attachment_1.filename = 'Instructions to Participants.docx'   
	subject = 'Final Confirmation for Oasis'
	from_email = Email('register@bits-oasis.org')
	sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
	for part in parts:	
		to_email = Email(part.email)
		body = """<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
			<center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!
Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 47th edition of OASIS, the annual cultural fest of Birla Institute of Technology & Science, Pilani, India. This year, OASIS will be held from October 31st to November 4th.             
           
This is to confirm your participation at OASIS '17.
We would be really happy to see your college represented at our fest.

We look forward to seeing you at OASIS 2017.
A new link would be active in your OASIS '17 account where you will find a profile card. A printed copy of the same is compulsory to enter the premises.

PFA A list of participants from your college.

Regards,
StuCCAn (Head)
Dept. of Publications & Correspondence, OASIS 2017
BITS Pilani
%s
pcr@bits-oasis.org

<b>Please reply to this email with number of people, if you require conveyance to or from Loharu and the timings for it.</b>
</pre>
			""" %(part.name,get_pcr_number())
		content = Content('text/html', body)
		try:
			mail = Mail(from_email, subject, to_email, content)
			mail.add_attachment(attachment)
			mail.add_attachment(attachment_1)
			response = sg.client.mail.send.post(request_body=mail.get())
			print 'Here'
			messages.warning(request,'Email sent to ' + part.name)
			part.pcr_final=True
			part.save()
			if not part.is_cr:
				encoded = gen_barcode(part)
				part.save()
		except Exception,e:
			print str(e)
			messages.warning(request,'Error sending email')
	return redirect(reverse('pcradmin:final_confirmation', kwargs={'c_id':college.id}))

@staff_member_required
def download_pdf(request, eg_id):
	try:
		_dir = '/root/live/oasis/backend/resources/oasis2017/'
		doc_name = _dir + 'final_list.pdf'
		a=create_final_pdf(eg_id, doc_name, _dir)
	except:
		_dir = '/home/auto-reload/Downloads/'
		doc_name = _dir + 'final_list.pdf'
		a=create_final_pdf(eg_id, doc_name, _dir)
	pdf = open(a, 'rb')
	response = HttpResponse(content_type='application/pdf', content=pdf)
	response['Content-Disposition'] = 'attachment; filename="final_list.pdf"'
	return response

###################################    Send final email ###################################
# def send_final_email
# DONT FORGET TO GENERATE BARCODES FOR THE PARTICIPANTS, ONLY NON CR PARTICIPANTS COZ MISSED FOR THEM IN MAIN REGISTRATIONS
############################################################################


@login_required
def user_logout(request):
	logout(request)
	return redirect('pcradmin:index')

@staff_member_required
def contacts(request):
	return render(request, 'pcradmin/contacts.html')

####  HELPER FUNCTIONS  ####
def participants_count(parts):
	x1 = len(parts)
	if x1 == 0:
		return '- - - - '
	x2 = parts.filter(cr_approved=True, email_verified=True).count()
	x3=parts.filter(pcr_approved=True).count()
	x4=parts.filter(Q(paid=True)|Q(curr_paid=True)).count()
	return str(x1) + ' | ' + str(x2) + ' | ' + str(x3) + ' | ' + str(x4)

def is_profile_complete(part):
	try:
		profile_url = part.profile_pic.url
		docs_url = part.verify_docs.url
		return True
	except:
		return False


def profile_stats(parts):
	x=parts.filter(pcr_approved=True).count()
	y=0
	for part in parts:
		if is_profile_complete(part):
			y+=1
	return str(x) + ' | ' + str(y)

def how_much_paid(part):
	if part.controlz_paid or part.curr_controlz_paid:
		return 950
	if part.paid or part.curr_paid:
		return 300
	return 0

def create_final_pdf(eg_id, response, _dir):
	email_group = EmailGroup.objects.get(id=eg_id)
	from reportlab.platypus.tables import Table
	from reportlab.lib import colors
	from reportlab.lib.units import inch
	from reportlab.lib.pagesizes import letter
	from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
	elements = []
	doc = SimpleDocTemplate(response, pagesize=letter)
	data = [('Name', 'Events', 'Payment')]
	for part in email_group.participant_set.all():
		events = ''
		for participation in Participation.objects.filter(participant=part, pcr_approved=True):
			events += participation.event.name + ', '
		events = events[:-2]
		amount = how_much_paid(part)
		data.append((part.name, events, amount))
	table_with_style = Table(data, [3 * inch, 1.5 * inch, inch])

	table_with_style.setStyle(TableStyle([
	    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
	    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
	    ('FONTSIZE', (0, 0), (-1, -1), 8),
	    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
	    ('BOX', (0, 0), (-1, 0), 0.25, colors.green),
	    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
	]))

	
	doc.build([Spacer(1, 0.5 * inch),table_with_style])
	watermark_name = _dir + 'Capture.pdf'
	output_file = PdfFileWriter()
	input_file = PdfFileReader(open(response, "rb"))
	page_count = input_file.getNumPages()
	for page_number in range(page_count):
		watermark = PdfFileReader(open(watermark_name, "rb"))
		input_page = watermark.getPage(0)
		input_page.mergePage(input_file.getPage(page_number))
		output_file.addPage(input_page)
	output_name = _dir +'final_pdf.pdf'
	with open(output_name, "wb") as outputStream:
		output_file.write(outputStream)
	return output_name


####  End of HELPER FUNCTIONS  ####