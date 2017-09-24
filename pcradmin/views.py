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
from registrations.sg_config import *
import string
from random import sample, choice
chars = string.letters + string.digits

from django.contrib import messages

@staff_member_required
def index(request):
	return render(request, 'pcradmin/index.html')

@staff_member_required
def college(request):
	rows = [{'data':[college.name,college.participant_set.filter(pcr_approved=True).count(),college.participant_set.all().count()],'link':[{'title':'Select', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})}] } for college in College.objects.all()]
	tables = [{'title':'List of Colleges', 'rows':rows, 'headings':['College', 'Total Participants','Confirmed', 'Select']}]
	return render(request, 'pcradmin/tables.html', {'tables':tables})

@staff_member_required
def select_college_rep(request, id):
	college = get_object_or_404(College, id=id)
	if request.method == 'POST':
		data = request.POST
		print data
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
			part.save()
		elif 'select' == data['submit']:
			try:
				Participant.objects.get(college=college,is_cr=True)
				return render(request, 'registrations/message.html', {'message':'You already have one College Representative selected. Delete him to modify.'})
			except:
				pass
			part = Participant.objects.get(id=part_id)
			part.is_cr=True
			part.save()
			user = part.user
			if not user == None:
				messages.warning(request,'College Representative already selected')
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


	participants = college.participant_set.all()
	try:
		cr = Participant.objects.get(college=college, is_cr=True)
		participants = participants.exclude(id=cr.id)
	except:
		cr=[]
	parts = [{'data':[part.name, part.phone, part.email, part.gender, part.pcr_approved, is_profile_complete(part)], "id":part.id,} for part in participants]
	return render(request, 'pcradmin/college_rep.html',{'college':college, 'parts':parts, 'cr':cr})




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
		return render(request, 'pcradmin/stats_home.html')
	if order=='collegewise':
		rows = []
		for college in College.objects.all():
			parts = college.participant_set.all()
			try:
				parts.filter(is_cr=True)[0]
				cr = True
			except:
				cr = False

			
			rows.append({'data':[college.name, cr, participants_count(parts)], 'link':[]})
		row.append({'data':['Total', ' ', participants_count(Participant.objects.all())], 'link':[]})
		headings = ['College', 'CR Selected', 'Stats']
		title = 'CollegeWise Participants Stats'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})


	if order == 'eventwise':
		rows = []
		for event in Event.objects.all():
			participations = Participation.objects.filter(event=event)
			parts = [p.participant for p in participations]
			parts_m = [p.participant for p in participations if p.participant.gender=='M']
			parts_f = [p.participant for p in participations if p.participant.gender=='F']
			rows.append({'data':[event.name, event.category, participants_count(parts_m), 
				participants_count(parts_f), participants_count(parts)], 'link':[]})
		parts = Participant.objects.all()
		parts_m  = Participant.objects.filter(gender='M')
		parts_f = Participant.objects.filter(gender='F')
		rows.append({'data':['Total', ' ', participants_count(parts), participants_count(parts_m), participants_count(parts_f)]})
		headings = ['Event', 'Category', 'Male', 'Female', 'Total']
		title = 'Eventwise Participants Stats'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})
	if order == 'paidwise':
		rows = [{'data':[part.name, part.college.name, part.gender, part.phone, part.email, part.paid], 'link':[]} for part in Participant.objects.filter(pcr_approved=True)]
		headings = ['Name', 'College', 'Sex', 'Phone', 'Email', 'Payment']
		title = 'Participants\' payment status'
		return render(request, 'pcradmin/tables.html', {'tables':[{'rows': rows, 'headings':headings, 'title':title}]})
	

@staff_member_required
def add_college(request):
	if request.method == 'POST':
		try:
			name = request.POST['name']
			if name=='':
				raise Exception
		except:
			messages.warning(request, 'Please Don\'t leave the name field empty')
			return redirect(request.META.get('HTTP_REFERER'))
		College.objects.create(name=name)
		messages.warning(request, 'College Succecfully added')
		return redirect('pcradmin:add_college')
	rows = [{'data':[college.name, college.participant_set.all().count(),  college.participant_set.filter(pcr_approved=True).count()], 'link':[{'title':'Select College Representative', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})}]} for college in College.objects.all()]
	headings = ['Name', 'Registered Participants' , 'PCr approved Participants', 'Select/Modify CR']
	title = "College List"
	table = {
		'rows':rows,
		'headings':headings,
		'title':title,
	}
	return render(request, 'pcradmin/add_college.html', {'table':table})

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

####  HELPER FUNCTIONS  ####
def participants_count(participants):
	x1 = len(participants)
	x2=x3=x4=0
	if x1 == 0:
		return '- - - -'
	for part in parts:
		if Participation.objects.get(participant=part).cr_confirmed:
			x2+=1
		if Participation.objects.get(participant=part).pcr_confirmed:
			x3+=1
		if part.paid:
			x4+=1
	return str(x1) + ' | ' + str(x2) + ' | ' + str(x3) + ' | ' + str(x4)

def is_profile_complete(part):
	try:
		profile_url = part.profile_pic.url
		docs_url = part.verify_docs.url
		return True
	except:
		return False
####  End of HELPER FUNCTIONS  ####