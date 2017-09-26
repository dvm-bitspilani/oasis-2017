from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse
from models import *
from events.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .forms import *
import sendgrid
import os
from sendgrid.helpers.mail import *
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo
import re
from oasis2017.keyconfig import *
from django.contrib.auth.models import User
import string
from random import sample, choice
chars = string.letters + string.digits

import requests

try:
	from oasis2017.config import *
	api = Instamojo(api_key=INSTA_API_KEY, auth_token=AUTH_TOKEN)
except:
	api = Instamojo(api_key=INSTA_API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/') #when in development

def home(request):
		if request.method == 'POST':
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					
					return redirect('registrations:index')
				else:
					context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional Contacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .'}
					return JsonResponse({'status':0, 'context':context})
			else:
				context = {'error_heading' : "Invalid Login Credentials", 'message' :  'Invalid Login Credentials. Please try again'}
				return JsonResponse({'status':0, 'context':context})

		else:
			return render(request, 'registrations/login.html')

@csrf_exempt
def prereg(request):

	if request.POST:
		print request.POST
		print hello
		name = request.POST['name']
		gender = request.POST['gender']
		if gender == "male":
			gender = 'M'
		elif gender == "female":
			gender = 'F'
		city = request.POST['city']
		email_id = request.POST['email_id'].lower().strip()
		college = request.POST['college']
		if college == 'Others':

			college = College()
			college.name = request.POST['other_college']
			college.is_displayed = False
			college.save()

		phone_no = int(request.POST['phone_no'])
		events = request.POST.getlist('events')
		
		if len(events) == 0:
			return JsonResponse({'status':1, 'message':'Register for atleast one event'})

		if IntroReg.objects.get(email_id=email_id).exists():
			return JsonResponse({'status':2,'message':'Email already registered.'})
		
		else:
			participant = IntroReg()
			participant.name = name
			participant.gender = gender
			participant.city = city
			participant.email_id = email_id
			participant.college = college
			participant.phone_no = phone_no
			participant.literacy = request.POST['literacy']
			participant.dance = request.POST['dance']
			participant.music = request.POST['music']
			participant.theatre = request.POST['theatre']
			participant.fashion_parade = request.POST['fashion_parade']
			participant.find_out_about_oasis = request.POST['oasis_info']
			participant.save()
			for key in events:
				event = Event.objects.get(id=int(key))
				participant.events.add(event)
			participant.save()

			college_list = College.objects.all()
			event_list = Event.objects.all()

			data = {'status':0,'email':email, 'name':name, 'mobile_number':mobile_number, 'college_list':college_list, 'event_list':event_list}
			return JsonResponse(data)

	college_list = College.objects.all()
	event_list = Event.objects.all()
	
	return render(request, 'registrations/index.html', {'college_list':college_list, 'event_list':event_list})

@csrf_exempt
def index(request):
	if request.user.is_authenticated():
		user = request.user
		participant = Participant.objects.get(user=user)
		participation_set = Participation.objects.filter(participant=participant)
		cr = Participant.objects.get(college=participant.college, is_cr=True)
		return render(request, 'registrations/home.html', {'participant':participant, 'participations':participation_set, 'cr':cr})

	if request.method == 'POST':
		data = request.POST
		recaptcha_response = data['g-recaptcha-response']
		data_1 = {
			'secret' : recaptcha_key,
			'response' : recaptcha_response
		}
		r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data_1)
		result = r.json()
		if not result['success']:
			return JsonResponse({'status':0, 'message':'Invalid Recaptcha. Try Again'})
		email = data['email']
		if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
			return JsonResponse({'status':0, 'message':'Please enter a valid email address.'})
		try:
			Participant.objects.get(email=data['email'])
			return JsonResponse({'status':0, 'message':'Email already registered.'})
		except:
			pass
		print data.getlist('events[]')
		if len(data.getlist('events[]')) == 0:
			return JsonResponse({'status':0, 'message':'Select atleast one event'})
		else:
			participant = Participant()
			participant.name = str(data['name'])
			participant.gender = str(data['gender'])
			participant.city = str(data['city'])
			participant.email = str(data['email'])
			participant.college = College.objects.get(name=str(data['college']))
			participant.phone = int(data['phone'])
			if str(data['head_of_society']) == 'True':
				participant.head_of_society = True
			else:
				participant.head_of_society = False
			participant.year_of_study = int(data['year_of_study'])
			participant.save()
			for key in data.getlist('events[]'):
				print int(key)
				event = Event.objects.get(id=int(key))
				Participation.objects.create(event=event, participant=participant)
			participant.save()


			send_to = str(request.POST["email"])
			name = str(request.POST["name"])
			body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
			<center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 47th edition of OASIS, the annual cultural fest of Birla Institute of Technology & Science, Pilani, India. This year, OASIS will be held from October 31st to November 4th.             

Please apply as soon as possible to enable us to confirm your participation at the earliest.             

We would be really happy to see your college represented at our fest.            

We look forward to seeing you at OASIS 2017.

<a href='%s'>Click Here</a> to verify your email.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT OASIS 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
StuCCAn (Head)
Dept. of Publications & Correspondence, OASIS 2017
BITS Pilani
+91-9828529994
pcr@bits-oasis.org
</pre>
			'''%(name, str(request.build_absolute_uri(reverse("registrations:index"))) + 'email_confirm/' + generate_email_token(Participant.objects.get(email=send_to)) + '/')

			# email = EmailMultiAlternatives("Registration for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("registrations:email_confirm", kwargs={'token':generate_email_token(GroupLeader.objects.get(email=send_to))})))  + '/' + ' to confirm.', 
			# 								'register@bits-bosm.org', [send_to.strip()]
			# 								)
			# email.attach_alternative(body, "text/html")
			sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
			from_email = Email('register@bits-oasis.org')
			to_email = Email(send_to)
			subject = "Registration for OASIS '17 REALMS OF FICTION"
			content = Content('text/html', body)
			print from_email, to_email
			try:
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())
			except :
				participant.delete()
				return JsonResponse({'status':0, 'message':'Error sending email. Please try again.'})
			print "Sent"
			message = "A confirmation link has been sent to %s. Kindly click on it to verify your email address." %(send_to)
			return JsonResponse({'status':1, 'message':message})
				
	else:
		colleges = College.objects.all()
		events = Event.objects.all()
		return render(request, 'registrations/signup.html', {'college_list':colleges, 'event_list':events})	


############# Helper functions for Django Email ##########

def generate_email_token(participant):

	import uuid
	token = uuid.uuid4().hex
	registered_tokens = [profile.email_token for profile in Participant.objects.all()]

	while token in registered_tokens:
		token = uuid.uuid4().hex

	participant.email_token = token
	participant.save()
	
	return token

def authenticate_email_token(token):

	try:
		participant = Participant.objects.get(email_token=token)
		participant.email_verified = True
		participant.save()
		return participant

	except :
		return False

def gen_barcode(part):
	part_id = part.id
	encoded = part.barcode
	if encoded == '':
		raise ValueError
	if encoded is not None:
		return encoded
	part_ida = "%04d" % int(part_id)
	college_code = ''.join(part.college.name.split(' '))
	if len(college_code)<4:
		college_code += str(0)*(4-len(college_code))
	encoded = ''.join([part_ida[i]+college_code[i] for i in range(0,4)])
	part.barcode = 'oasis17' + encoded
	part.save()
	import qrcode
	part_code = qrcode.make(barcode)
	try:
		image='/root/live/oasis/backend/resources/oasis2017/qrcodes/%04s.png' % int(part_id)
		part_code.save(image, 'PNG')
	except:
		image = '/home/auto-reload/Desktop/barcodes/participants/%04s.png' % int(part_id)
		part_code.save(image, 'PNG')
	return encoded
################################# End of helper functions ###############################

def email_confirm(request, token):
	member = authenticate_email_token(token)
	
	if member:
		context = {
			'error_heading': 'Email verified',
			'message': 'Your email has been verified. Please wait for further correspondence from the Department of PCr, BITS, Pilani',
			'url':'https://bits-oasis.org'
		}
	else:
		context = {
			'error_heading': "Invalid Token",
			'message': "Sorry! This is an invalid token. Email couldn't be verified. Please try again.",
			'url':'https://bits-oasis.org'
		}
	return render(request, 'registrations/message.html', context)

@login_required
def cr_approve(request):
	user = request.user
	participant = Participant.object.get(user=user)
	if not participant.is_cr:
		context = {
		'status': 0,
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		}
		return render(request, 'registrations/message.html', context)
	approved_list = Participation.objects.filter(participant__college=participant.college, cr_approved=True)
	disapproved_list = Participation.objects.filter(participant__college=participant.college, cr_approved=False)
	if request.method == 'POST':
		data = request.POST
		if 'approve' == data['action']:
			try:
				parts_id = data.getlist('parts_id')
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			for part_id in parts_id:
				participation = Participation.objects.get(id=part_id, participant__college=participant.college)
				participation.cr_approved = True
				participation.save()
				appr_participant = participation.participant
				if appr_participant.user is not None:
					user = appr_participant.user
					if not user.is_active:
						user.is_active = True
						user.save()
				else:
					username = appr_participant.name.split(' ')[0] + str(appr_participant.id)
					password = ''.join(choice(chars) for _ in xrange(8))
					user = User.objects.create_user(username=username, password=password)
					appr_participant.user = user
					appr_participant.save()

					send_to = appr_participant.email
					name = appr_participant.name
					body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
			<center><img src="http://bits-bosm.org/2016/static/docs/email_header.jpg"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 32nd edition of BITS Open Sports Meet (BOSM), the annual national sports meet of Birla Institute of Technology & Science, Pilani, India. This year, BOSM will be held from September 21st to 25th.             

 Applications close on 31st August 2017 at 1700 hrs.            

Please apply as soon as possible to enable us to confirm your participation at the earliest.             

We would be really happy to see your college represented at our sports festival.            

We look forward to seeing you at BOSM 2017.

Your login credentials are as follows:
Username : %s
Password : %s

The credentials are randomly generated and hence possess no relation with any entity. Do not share them with anyone.
P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT BOSM 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
CoSSAcn (Head)
Dept. of Publications & Correspondence, BOSM 2017
BITS Pilani
+91-9929022741
pcr@bits-bosm.org
</pre>
			'''		%(name, username, password)
					sg = sendgrid.SendGridAPIClient(apikey=INSTA_API_KEY)
					from_email = Email('register@bits-oasis.org')
					to_email = Email(send_to)
					subject = "Registration for OASIS '17 REALMS OF FICTION"
					content = Content('text/html', body)

					try:
						mail = Mail(from_email, subject, to_email, content)
						response = sg.client.mail.send.post(request_body=mail.get())
					except :
						appr_participant.user = None
						appr_participant.save()
						user.delete()
						context = {
							'status': 0,
							'error_heading': "Error sending mail",
							'message': "Sorry! Error in sending email. Please try again.",
						}
						return render(request, 'registrations/message.html', context)

			context = {
				'error_heading': "Emails sent",
				'message': "Login credentials have been mailed to the corresponding new participants.",
			}
			return render(request, 'registrations/message.html', context)


		if 'disapprove' == data['action']:
			try:
				parts_id = data.getlist('parts_id')
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			for part_id in parts_id:
				participation = Participation.objects.get(id=part_id, participant__college=participant.college)
				participation.cr_approved = False
				participation.pcr_approved = False
				participation.save()
	return render(request, 'registrations/cr_approve.html', {'approved_list':approved_list, 'disapproved_list':disapproved_list})

@login_required
def edit_participant(request):
	participant = Participant.objects.get(user=request.user)
	if request.method == 'POST':
		data = request.POST
		name = data['name']
		phone = data['phone']
		participant.name = name
		participant.phone = phone
		participant.save()
	return render(request, 'registrations/participant_edit.html', {'participant':participant})

@login_required
def participant_details(request, p_id):
	user = request.user
	participant = Participant.object.get(user=user)
	if not participant.is_cr:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		'url':request.build_absolute_uri(reverse('registrations:home'))
		}
		return render(request, 'registrations/message.html', context)
	get_part = Participant.objects.get(id=p_id)
	if not get_part.college == participant.college:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You do not have access to these details.",
		'url':request.build_absolute_uri(reverse('registrations:home'))
		}
		return render(request, 'registrations/message.html', context)
	participation_list = Participation.objects.filter(participant=get_part)
	return render(request, 'registrations/home.html', {'participant':get_part, 'participations':participation_list})

@login_required
def participant_payment(request):
	participant = Participant.objects.get(user=request.user)
	if request.method == 'POST':
		if int(request.POST['key']) == 1:
			amount = 300
		elif int(request.POST['key']) == 2:
			amount = 950
		name = participant.name
		email = participant.email
		phone = participant.phone
		purpose = 'Payment for OASIS \'17'
		response = api.payment_request_create(buyer_name= name,
							email= email,
							phone= number,
							amount = amount,
							purpose=purpose,
							redirect_url= request.build_absolute_uri(reverse("registrations:API Request"))
							)
		# print  email	, response['payment_request']['longurl']			
		try:
			url = response['payment_request']['longurl']
			return HttpResponseRedirect(url)
		except:
			context = {
				'error_heading': "Payment error",
				'message': "An error was encountered while processing the request. Please contact PCr, BITS, Pilani.",
				}
			return render(request, 'registrations/message.html')
	else:
		return render(request, 'registrations/participant_payment.html', {'participant':participant})

@login_required
def manage_events(request):
	participant = Participant.objects.get(user=request.user)
	if request.method == 'POST':
		data = request.POST
		if 'add' == data['action']:
			try:
				events_id = data.getlist('events_id')
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			for event_id in events_id:
				event = Event.objects.get(id=event_id)
				Participation.objects.create(participant=participant, event=event)

		if 'remove' == data['action']:
			try:
				events_id = data.getlist('events_id')
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			for event_id in events_id:
				try:
					event = Event.objects.get(id=event_id)
					participation = Participation.objects.get(participant=participant, event=event)
					participation.delete()
				except:
					pass
	added_list = [participation.event for participation in Participation.objects.filter(participant=participant)]
	not_added_list = [event for event in Event.objects.all() if event not in added_list]
	return render(request, 'registrations/manage_events.html', {'added_list':added_list, 'not_added_list':not_added_list}) 

@login_required
def cr_payment(request):
	user = request.user
	participant = Participant.object.get(user=user)
	if not participant.is_cr:
		context = {
		'status': 0,
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		}
		return render(request, 'registrations/message.html', context)
	if request.method == 'POST':
		data = request.POST
		if int(request.POST['key']) == 1:
			amount = 300
		elif int(request.POST['key']) == 2:
			amount = 950
		part_list = Participant.objects.filter(id__in=data.getlist('part_list'))
		group = PaymentGroup()
		group.amount_paid = amount*len(part_list)
		group.save()
		for part in part_list:
			part.payment_group = group
			part.save()
		name = participant.name
		email = participant.email
		phone = participant.phone
		purpose = 'Payment ' + str(group.id)
		response = api.payment_request_create(buyer_name= name,
						email= email,
						phone= number,
						amount = group.amount_paid,
						purpose=purpose,
						redirect_url= request.build_absolute_uri(reverse("registrations:API Request"))
						)
	# print  email	, response['payment_request']['longurl']			
		try:
			url = response['payment_request']['longurl']
			return HttpResponseRedirect(url)
		except:
			group.delete()
			context = {
				'error_heading': "Payment error",
				'message': "An error was encountered while processing the request. Please try again or contact PCr, BITS, Pilani.",
				}
			return render(request, 'registrations/message.html')

	else:
		participant_list = Participant.objects.filter(college=participant.college, pcr_approved=True, paid=False)
		return render(request, 'cr_payment.html', {'participant_list':participant_list})

@login_required
def upload_docs(request):
	participant = Participant.object.get(user=request.user)
	if request.method == 'POST':
		try:
			image = participant.profile_pic
			if image is not None:
				image.delete(save=True)
			new_img = request.FILES['profile_pic']
			participant.profile_pic = new_img
			participant.save()
		except:
			pass
		try:
			docs = participant.verify_docs
			if docs is not None:
				docs.delete(save=True)
			new_docs = request.FILES['verify_docs']
			participant.verify_docs = new_docs
			participant.save()
		except:
			pass
	return render(request, 'registrations/upload_docs.html', {'participant':participant})

def apirequest(request):
	import requests
	payid=str(request.GET['payment_request_id'])
	headers = {'X-Api-Key': INSTA_API_KEY,
    	       'X-Auth-Token': AUTH_TOKEN}
	try:
		from oasis2017.config import *
   		r = requests.get('https://www.instamojo.com/api/1.1/payment-requests/'+str(payid),headers=headers)
	except:
		r = requests.get('https://test.instamojo.com/api/1.1/payment-requests/'+str(payid), headers=headers)    ### when in development
	json_ob = r.json()
	if (json_ob['success']):
		payment_request = json_ob['payment_request']
		purpose = payment_request['purpose']
		amount = payment_request['amount']
		try:
			group_id = int(purpose.split(' ')[1])
			payment_group = PaymentGroup.objects.get(id=group_id)
			count = payment_group.participant_set.all().count()
			for part in payment_group.participant_set.all():
				part.paid = True
				if (amount/count) == 950:
					part.controlz_paid = True
				part.save()

		except:		
			email = payment_request['email']
			participant = Participant.objects.get(email=email)
			participant.paid = True
			if amount == 950:
				participant.controlz_paid = True
			participant.save()
		message = "Payment successful"
		return render(request, 'registrations/message.html', )
	
	else:

		payment_request = json_ob['payment_request']
		purpose = payment_request['purpose']
		email = payment_request['email']
		context = {
			'error_heading': "Payment error",
			'message': "An error was encountered while processing the payment. Please contact PCr, BITS, Pilani.",
			}
		return render(request, 'registrations/message.html')

@staff_member_required
def event_list(request, event):

	from django.http import HttpResponse, HttpResponseRedirect, Http404
	import xlsxwriter
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO

	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('new-spreadsheet')
	date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
	worksheet.write(0, 0, "Generated:")
	from time import gmtime, strftime
	generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
	worksheet.write(0, 1, generated)
	x=2

	try:
		event = Event.objects.get(name=str(event))
	
	except:
		raise Http404("Event name not among : StandUp, Rocktaves, RapWars, StreetDance, PitchPerfect")

	participant_list = IntroReg.objects.filter(event in event_list)

	su_list = [{'obj': i} for i in participant_list]

	if su_list:
		worksheet.write(x, 0, "Required List")
		x+=1
		worksheet.write(x, 0, "S.No.")
		worksheet.write(x, 1, "Name")
		worksheet.write(x, 2, "City")
		worksheet.write(x, 3, "Phone No.")
		worksheet.write(x, 4, "Gender")
		worksheet.write(x, 5, "Email ID")
		x+=1
		for i, row in enumerate(su_list):
			worksheet.write(i+x, 0, i)			
			worksheet.write(i+x, 1, deepgetattr(row['obj'], 'name', 'NA'))
			worksheet.write(i+x, 2, deepgetattr(row['obj'], 'city', 'NA'))
			worksheet.write(i+x, 3, deepgetattr(row['obj'], 'phone', 'NA'))
			worksheet.write(i+x, 4, deepgetattr(row['obj'], 'gender', 'NA'))
			worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_id', 'NA'))
		x+=len(su_list)+2

	workbook.close()
	filename = 'ExcelReport' + event + '.xlsx'
	output.seek(0)
	response = HttpResponse(output.read(), content_type="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

@staff_member_required
def college_list(request, pk):

	from django.http import HttpResponse, HttpResponseRedirect, Http404
	import xlsxwriter
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO

	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('new-spreadsheet')
	date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
	worksheet.write(0, 0, "Generated:")
	from time import gmtime, strftime
	generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
	worksheet.write(0, 1, generated)
	x=2

	try:
		college = College.objects.get(pk=pk)
	
	except:
		raise Http404("College data absent.")

	participant_list = college.introreg_set.all()

	su_list = [{'obj': i} for i in participant_list]
	if su_list:
		worksheet.write(x, 0, "Required List")
		x+=1
		worksheet.write(x, 0, "S.No.")
		worksheet.write(x, 1, "Name")
		worksheet.write(x, 2, "City")
		worksheet.write(x, 3, "Phone No.")
		worksheet.write(x, 4, "Gender")
		worksheet.write(x, 5, "Email ID")
		x+=1
		for i, row in enumerate(su_list):
			worksheet.write(i+x, 0, i)			
			worksheet.write(i+x, 1, deepgetattr(row['obj'], 'name', 'NA'))
			worksheet.write(i+x, 2, deepgetattr(row['obj'], 'city', 'NA'))
			worksheet.write(i+x, 3, deepgetattr(row['obj'], 'phone', 'NA'))
			worksheet.write(i+x, 4, deepgetattr(row['obj'], 'gender', 'NA'))
			worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_id', 'NA'))
		x+=len(su_list)+2

	workbook.close()
	filename = 'ExcelReport-' + college.name + '.xlsx'
	output.seek(0)
	response = HttpResponse(output.read(), content_type="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

def deepgetattr(obj, attr, default = None):
    
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise
    return obj