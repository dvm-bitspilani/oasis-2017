from django.shortcuts import render, get_object_or_404, get_list_or_404
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

import string
from random import sample, choice
chars = string.letters + string.digits

@staff_member_required
def index(request):
	return render(request, 'pcradmin/index.html')

@staff_member_required
def college(request):
	rows = [{'data':[college.name,college.participants.all().count()],'link':[{'title':'Select', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})}] } for college in College.objects.all()]
	tables = [{'title':'Select a College to add CR', 'rows':rows, 'headings':['College', 'Total Participants', 'Select']}]
	return render(request, 'pcradmin/tables.html', {'tables':tables})

@staff_member_required
def select_college_rep(request, id):
	college = get_object_or_404(College, id=id)
	if request.method == 'POST':
		data = request.POST
		part_id = data['data']
		if 'delete' == data['submit']:
			part = Participants.objects.get(id=part_id)
			part.user.is_active = False
			part.is_cr=False
			part.save()
		elif 'select' == data['submit']:
			try:
				Participant.objects.get(college=college,is_cr=True)
				return render(request, 'registrations/message.html', {'message':'You already have one College Representative selected. Delete him to modify.'})
			except:
				pass
			part = Participants.objects.get(id=part_id)
			part.is_cr=True
			part.save()
			user = part.user
			if user is None:
				user = User.objects.create(username=username, password='')
				username = part.name.split(' ')[0] + str(part_id)
				length = 8
				password = ''.join(choice(chars) for _ in xrange(length)) 
				user.set_password(password)
				user.save()
				part.user = user
				part.save()
			body = """
This is to inform you that you have been selected as the College Representative for your college.
username : '%s'
password : '%s'
Now you can login at <a href='bits-oasis.org/2017/registrations/'>bits-oasis.org/2017/registrations/ and see the list of participants of who have registered from your college.
It is your responsibility to confirm the participants for different events.

Regards,
Ashay Anurag
CoSSAcn (Head)
Dept. of Publications & Correspondence, BOSM 2017
BITS Pilani
+91-9929022741
			""" %(username, password)
			subject = 'College Representative for Oasis'
			from_email = Email('register@bits-oasis.org')
			to_email = Email(part.email)
			content = Content('text/html', body)
			try:
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())
				return render(request, 'pcradmin/message.html', {'message':'Emails sent'})
			except :
				part.user = None
				user.delete()
				part.save()
				return render(request, 'pcradmin/message.html', {'message':'Email not sent. Please select College Representative again.'})


		# return redirect('pcradmin:college_rep'
	participants = college.participant_set.all()
	try:
		cr = Participant.objects.get(college=college, is_cr=True)
		participants = participants.exclude(id=cr.id)
	except:
		cr=[]
	parts = [{'data':[part.name, part.phone, part.email, part.gender, part.pcr_approved], "id":part.id, 'verfiy':reverse('pcradmin:verify_profile', kwargs={'id':part.id})} for part in participants]

	return render(request, 'pcradmin/college_rep.html',{'college':college, 'parts':parts, 'cr':cr})

@staff_member_required
def verify_profile(request, part_id):
	part = Participant.objects.get(id=part_id)

	if request.method=='POST':
		data = dict(request.POST)['data']
		if not data:
			return redirect(request.META.get('HTTP_REFERER'))

		if request.POST['submit'] == 'confirm':
			Participation.objects.filter(id__in=data, cr_approved=True).update(pcr_approved=True)
			part.pcr_approved = True
		elif request.POST['submit'] == 'unconfirm':
			Participation.objects.filter(id__in=data, cr_approved=True).update(pcr_approved=False)
			if all([p.pcr_approved for p in Participation.objects.filter(participant=part)]):
				part.pcr_approved=False
		part.save()

		return redirect(reverse('select_college_rep', kwargs={'id':part.college.id}))
	try:
		profile_url = part.profile_pic.url
		docs_url = part.verify_docs.url
	except:
		message = 'Profile not complete yet.'
		return render(request, 'pcradmin/meesage.html', {'message':message})
	participations = Participant.participation_set.all()
	events_confirmed = [{'event':p.event, 'id':p.id} for p in participations.filter(pcr_approved=True)]
	events_unconfirmed = [{'event':p.event, 'id':p.id} for p in participations.filter(pcr_approved=False)]
	return render(request, 'pcradmin/verify_profile.html',
	{'profile_url':profile_url, 'docs_url':docs_url, 'part':part, 'confirmed':events_confirmed, 'unconfirmed':events_unconfirmed})


################################ STATS ########################################3

@staff_member_required
def stats(request):
	if order=='collegewise':
		rows = []
		for college in College.objects.all():
			parts = college.participant_set.all()
			try:
				parts.filter(is_cr=True)[0]
				cr = True
			except:
				cr = False

			x1 = parts.count()
			if x1==0:
				rows.append({'data':[college.name, cr, '- - - -'], 'link':[]})
				continue
			x2=x3=x4=0
			for part in parts:
				if Participation.objects.get(participant=part).cr_confirmed:
					x2+=1
				if Participation.objects.get(participant=part).pcr_confirmed:
					x3+=1
				if part.paid:
					x4+=1
			data = str(x1) + ' | ' + str(x2) + ' | ' + str(x3) + ' | ' + str(x4)
			rows.append({'data':[college.name, cr, data], 'link':[]})
		headings = ['College', 'CR Selected', 'Stats']
		title = 'CollegeWise Participants list'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})
	if order == 'eventwise':
		rows = []
		for event in Event.objects.all():
			participations = Participation.objects.filter(event=event)
			parts = [p.participant for p in participations]
			x1 = parts.count()
			if x1==0:
				rows.append({'data':[event.name, event.categoryentry['cr'], '- - - -'], 'link':[]})
				continue
			x2=x3=x4=0


@staff_member_required
def add_college(request):
	if request.method == 'POST':
		name = request.POST['name']
		College.objects.create(name=name)
	rows = [{'data':[college.name, college.participant_set.all().count(), college.partcipant_set.filter(pcr_approved=True).count()], 'link':[{'title':'Select College Representative', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})}]} for college in College.objects.all()]
	headings = ['Name', 'Registered Participants' , 'CR-approved Participants', 'PCr approved Participants', 'Select/Modify CR']
	title = "College List"
	table = {
		'rows':rows,
		'headings':headings,
		'title':title,
	}
	return render(request, 'pcradmin/add_college.html', {'tables':[table, ],})

@staff_member_required
def pcr_final_confirmation(request):
	if request.method == 'POST':
		data = request.POST
		id_list = data.getlist('college_list')
		college_list = College.objects.filter(id__in=id_list)
		for college in college_list:
			cr = Participant.objects.get(college=college, is_cr=True)
			send_to = cr.email
			name = cr.name
			body = '''
				<Email Body>
			'''
			subject = 'Final Confirmation for OASIS \'17:REALMS OF FICTION'
			sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
			from_email = Email("no-reply@bits-oasis.org")
			to_email = Email(send_to)
			content = Content("text/html", )

			Participant.objects.filter(college=college, pcr_approved=True).update(pcr_final=True)

			try:
				mail = Mail(from_email, subject, to_email, content)
				mail.add_attachment(attachment1)
				mail.add_attachment(attachment2)
				response = sg.client.mail.send.post(request_body=mail.get())
			except:
				return render(request, 'pcradmin/message.html', {'message':'Email sending failed.'})
		
		return render(request, 'pcradmin/message.html', {'message':'Emails successfully sent.'})


def user_logout(request):
	logout(user)
	return redirect('pcradimn:home')

def contacts(request):
	return render(requsest, 'pcradmin/contacts.html')

