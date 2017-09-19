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
def home(request):
	return render(request, 'pcradmin/home.html')

@staff_member_required
def college(request):
	rows = [{'data':[college.name,college.participants.all().count()],'link':[{'title':'Select', 'url':reverse('pcradmin:select_college_rep', kwargs={'id':college.id})}] } for college in College.objects.all()]
	tables = [{'title':'Select a College to add CR', 'rows':rows, 'headings':['College', 'Total Participants', 'Select']}]
	return render(request, 'pcradmin/tables.html', {'tables':tables})

@staff_member_required
def select_college_rep(request, id):
	if request.method == 'POST':
		data = request.POST
		part_id = data['data']
		if 'delete' == data['submit']:
			part = Participants.objects.get(id=part_id)
			part.user.is_active = False
			part.is_cr=False
		elif 'select' == data['submit']:
			part = Participants.objects.get(id=part_id)
			part.is_cr=True
			part.save()
			user = part.user
			if not user:
				user = User.objects.create(username=username, password='')
				username = part.name.split(' ')[0] + str(part_id)

			length = 8
			password = ''.join(choice(chars) for _ in xrange(length)) 
			user.set_password(password)
			user.save()
			part.user = user
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
				return render(request, 'pcradmin/message.html', {'message':'Email not sent'})



		# return redirect('pcradmin:college_rep')
	college = get_object_or_404(College, id=id)
	participants = college.participants.all()
	try:
		cr = college.participants.filter(is_cr=True)[0]
		participants = participants.exclude(id=cr.id)
	except:
		cr=[]
	parts = [{'data':[part.name, part.phone, part.email, part.gender, part.pcr_approved], "id":part.id, 'verfiy':reverse('pcradmin:verify_profile', kwargs={'id':part.id})} for part in participants]

	return render(request, 'pcradmin/college_rep.html',{'college':college, 'parts':parts, 'cr':cr})

@staff_member_required
def verify_profile(request, part_id):
	part = Participant.objects.get(id=part_id)

	if request.method=='POST':
		part.pcr_approved = True
		part.save()
		return redirect(reverse('select_college_rep', kwargs={'id':part.college.id}))
	try:
		profile_url = part.profile_pic.url
		docs_url = part.verify_docs.url
	except:
		message = 'Profile not complete yet.'
		return render(request, 'pcradmin/meesage.html', {'message':message})

	return render(request, 'pcradmin/verify_profile.html', {'profile_url':profile_url, 'docs_url':docs_url})

def user_logout(request):
	logout(user)
	return redirect('pcradimn:home')

def contacts(request):
	return render(requsest, 'pcradmin/contacts.html')