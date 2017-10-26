from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse
from models import *
from events.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
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
from django.contrib import messages
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
				if not user.participant.email_verified:
					context = {'error_heading' : "Email not verified", 'message' :  'It seems you haven\'t verified your email yet. Please verify it as soon as possible to proceed. For any query, call the following members of the Department of Publications and Correspondence. Asim Shah: %s - pcr@bits-oasis.org .'%(get_pcr_number()), 'url':request.build_absolute_uri(reverse('registrations:home'))}
					return render(request, 'registrations/message.html', context)
				login(request, user)
				return redirect('registrations:index')
			else:
				context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Asim Shah: %s - pcr@bits-bosm.org .'%(get_pcr_number()), 'url':request.build_absolute_uri(reverse('registrations:home'))}
				return render(request, 'registrations/message.html', context)
		else:
			messages.warning(request,'Invalid login credentials')
			return redirect(request.META.get('HTTP_REFERER'))
	else:
		return render(request, 'registrations/login.html')

@csrf_exempt
def prereg(request):

	if request.POST:
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
			print(response.status_code)
			print(response.body)
			print(response.headers)
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
	part_code = qrcode.make(part.barcode)
	try:
		image='/root/live/oasis/backend/resources/oasis2017/qrcodes/%04s.png' % int(part_id)
		part_code.save(image, 'PNG')
	except:
		image = '/home/tushar/barcodes/participants/%04s.png' % int(part_id)
		part_code.save(image, 'PNG')
	return encoded

def get_pcr_number():
	number_list = ['8209182501', '7073180405', '7023611971', '9166947424', '9119225593', '9119225134', '9119225189', '9119225102', '9119225645']
	from random import randint
	return number_list[randint(0,8)]
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
	participant = Participant.objects.get(user=user)
	if not participant.is_cr:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		'url':request.build_absolute_uri(reverse('registrations:home'))
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
				participant_1 = participation.participant
				participant_1.cr_approved = True
				participant_1.save()
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
			<center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 47th edition of OASIS, the annual cultural fest of Birla Institute of Technology & Science, Pilani, India. This year, OASIS will be held from October 31st to November 4th.             
           
This is to inform you that your college representative has selected your participation.
You can now login <a href="%s">here</a> using the following credentials:
username : '%s'
password : '%s'
We would be really happy to see your college represented at our fest.

Please make sure to upload your <b>Picture</b> as well as <b>verification documents(Eg Bonafide)</b> once you login to complete your registration.

We look forward to seeing you at OASIS 2017.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT OASIS 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
StuCCAn (Head)
Dept. of Publications & Correspondence, OASIS 2017
BITS Pilani
%s
pcr@bits-oasis.org
</pre>
			''' %(name,str(request.build_absolute_uri(reverse('registrations:home'))),username, password, get_pcr_number())
					sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
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
						participation.cr_approved = False
						participation.save()
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
				participant_1 = participation.participant
				if all(not i.cr_approved for i in participant_1.participation_set.all()):
					participant_1.cr_approved = False
					participant_1.save()
	return render(request, 'registrations/cr_approval.html', {'approved_list':approved_list, 'disapproved_list':disapproved_list, 'participant':participant})

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
	participant = Participant.objects.get(user=user)
	if not participant.is_cr:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		'url':request.build_absolute_uri(reverse('registrations:index'))
		}
		return render(request, 'registrations/message.html', context)
	get_part = Participant.objects.get(id=p_id)
	if not get_part.college == participant.college:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You do not have access to these details.",
		'url':request.build_absolute_uri(reverse('registrations:index'))
		}
		return render(request, 'registrations/message.html', context)
	participation_list = Participation.objects.filter(participant=get_part)
	return render(request, 'registrations/profile.html', {'get_part':get_part, 'participations':participation_list, 'participant':participant})

@login_required
def participant_payment(request):
	participant = Participant.objects.get(user=request.user)
	if not participant.pcr_approved:
		context = {
		'error_heading': "Invalid Access",
		'message': "You are yet not approved by Department of PCr, Bits Pilani.",
		'url':request.build_absolute_uri(reverse('registrations:index'))
		}
		return render(request, 'registrations/message.html', context)
	if request.method == 'POST':
		try:
			key = request.POST['key']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		if int(request.POST['key']) == 1:
			amount = 300
		elif int(request.POST['key']) == 2:
			amount = 950
		elif int(request.POST['key']) == 3:
			amount = 650
		else:
			return redirect(request.META.get('HTTP_REFERER'))
		name = participant.name
		email = participant.email
		phone = participant.phone
		purpose = 'Payment for OASIS \'17'
		response = api.payment_request_create(buyer_name= name,
							email= email,
							phone= phone,
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
				'url':request.build_absolute_uri(reverse('registrations:make_payment'))
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
				p, created  = Participation.objects.get_or_create(participant=participant, event=event)

		if 'remove' == data['action']:
			try:
				events_id = data.getlist('events_id')
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			for event_id in events_id:
				try:
					event = Event.objects.get(id=event_id)
					participation = Participation.objects.get(participant=participant, event=event)
					if not participation.pcr_approved:
						participation.delete()
				except:
					pass
	added_list = [participation for participation in Participation.objects.filter(participant=participant)]
	added_events = [p.event for p in added_list]
	not_added_list = [event for event in Event.objects.all() if event not in added_events]
	return render(request, 'registrations/manage_events.html', {'added_list':added_list, 'not_added_list':not_added_list, 'participant':participant}) 

@login_required
def cr_payment(request):
	user = request.user
	participant = Participant.objects.get(user=user)
	if not participant.is_cr:
		context = {
		'status': 0,
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		}
		return render(request, 'registrations/message.html', context)
	if request.method == 'POST':
		data = request.POST
		try:
			key = int(data['key'])
			part_list = data.getlist('part_list')
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		if key == 1:
			amount = 300
		elif key == 2:
			amount = 950
		elif key == 3:
			amount = 650
		part_list = Participant.objects.filter(id__in=data.getlist('part_list'), pcr_approved=True)
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
		response = api.payment_request_create(buyer_name = name,
						email = email,
						phone = phone,
						amount = group.amount_paid,
						purpose = purpose,
						redirect_url = request.build_absolute_uri(reverse("registrations:API Request"))
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
				'url':request.build_absolute_uri(reverse('registrations:cr_payment'))
				}
			return render(request, 'registrations/message.html', context)

	else:
		participant_list = Participant.objects.filter(college=participant.college,paid=False, pcr_approved=True)
		prereg_list = Participant.objects.filter(college=participant.college, paid=True, controlz_paid=False)
		paid_list = Participant.objects.filter(college=participant.college, paid=True, controlz_paid=True)
		return render(request, 'registrations/cr_payment.html', {'participant_list':participant_list, 'participant':participant, 'prereg_list':prereg_list, 'paid_list':paid_list})

@login_required
def upload_docs(request):
	participant = Participant.objects.get(user=request.user)
	if request.method == 'POST':
		from django.core.files import File
		if participant.pcr_approved:
			context = {
					'error_heading': "Permission Denied",
					'message': "You have already been approved by PCr, BITS Pilani as a partcipant. Contact pcr@bits-oasis.org to change your uploads.",
					'url':request.build_absolute_uri(reverse('registrations:index'))
					}
			return render(request, 'registrations/message.html', context)
		try:
			image = request.FILES['profile_pic']
			print 'here'
			image = participant.profile_pic
			if image is not None:
				image.delete(save=True)
			up_img = request.FILES['profile_pic']
			img_file = resize_uploaded_image(up_img, 240, 240)
			new_img = File(img_file)
			participant.pcr_approved = False
			participant.profile_pic.save('profile_pic', new_img)
		except:
		 	pass
		try:
			verify_docs = request.FILES['verify_docs']
			print 'here1'
			docs = participant.verify_docs
			if docs is not None:
				docs.delete(save=True)
			up_docs = request.FILES['verify_docs']
			doc_file = resize_uploaded_image(up_docs, 400, 400)
			new_docs = File(doc_file)
			participant.pcr_approved = False
			participant.verify_docs.save('verify_docs', new_docs)
		except:
			pass
	try:
		image_url = request.build_absolute_uri('/')[:-1] + participant.profile_pic.url
		image = True
		print image_url
	except:
		image_url = '#'
		image = False
		pass
	try:
		docs_url = request.build_absolute_uri('/')[:-1] + participant.verify_docs.url
		docs = True
		print docs_url
	except:
		docs_url = '#'
		docs = False
		pass
	return render(request, 'registrations/upload_docs.html', {'participant':participant, 'image_url':image_url, 'image':image, 'docs_url':docs_url, 'docs':docs})

@login_required
def get_profile_card(request):
	participant = Participant.objects.get(user=request.user)
	if not participant.pcr_final:
		if not participant.is_guest:
			context = {
					'error_heading': "Invalid Access",
					'message': "Please complete your profile and make payments to access this page.",
					'url':request.build_absolute_uri(reverse('registrations:index'))
					}
			return render(request, 'registrations/message.html', context)
	participant = Participant.objects.get(user=request.user)
	participation_set = Participation.objects.filter(participant=participant, pcr_approved=True)
	events = ''
	for participation in participation_set:
		events += participation.event.name + ', '
	events = events[:-2]
	return render(request, 'registrations/profile_card.html', {'participant':participant, 'events':events,})

@login_required
def get_profile_card_cr(request, p_id):
	user = request.user
	participant = Participant.objects.get(user=user)
	if not participant.is_cr:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You are not an approved college representative.",
		'url':request.build_absolute_uri(reverse('registrations:index'))
		}
		return render(request, 'registrations/message.html', context)
	get_part = Participant.objects.get(id=p_id)
	if not get_part.college == participant.college:
		context = {
		'error_heading': "Invalid Access",
		'message': "Sorry! You do not have access to these details.",
		'url':request.build_absolute_uri(reverse('registrations:index'))
		}
		return render(request, 'registrations/message.html', context)
	if not get_part.pcr_final:
		context = {
				'error_heading': "Invalid Access",
				'message': "Please complete the participant's profile and make payments to access this page.",
				'url':request.build_absolute_uri(reverse('registrations:index'))
				}
		return render(request, 'registrations/message.html', context)
	participation_set = Participation.objects.filter(participant=get_part, pcr_approved=True)
	events = ''
	for participation in participation_set:
		events += participation.event.name + ', '
	events = events[:-2]
	return render(request, 'registrations/profile_card.html', {'participant':get_part, 'events':events,})
##################### HELPER FUNCTIONS FOR PROFILE CARD ##############################
def resize_uploaded_image(buf, height, width):
    
	import StringIO
	from PIL import Image
	image = Image.open(buf)
	width = width
	height = height
	resizedImage = image.resize((width, height))

	# Turn back into file-like object
	resizedImageFile = StringIO.StringIO()
	resizedImage.save(resizedImageFile , 'JPEG', optimize = True)
	resizedImageFile.seek(0)    # So that the next read starts at the beginning

	return resizedImageFile

def return_qr(request):
    text = request.GET.get('text')
    qr = generate_qr_code(text)
    response = HttpResponse(content_type="image/jpeg")
    qr.save(response, "JPEG")
    return response

def generate_qr_code(data):
	import qrcode
	import qrcode.image.svg
	from PIL import Image
	part_code = qrcode.make(data)
	# part_code = 
	return part_code
########################### END OF HELPER FUNCTIONS ############################33

def apirequest(request):
	import requests
	payid=str(request.GET['payment_request_id'])
	headers = {'X-Api-Key': INSTA_API_KEY,
    	       'X-Auth-Token': AUTH_TOKEN}
	try:
		from oasis2017 import config
   		r = requests.get('https://www.instamojo.com/api/1.1/payment-requests/'+str(payid),headers=headers)
	except:
		r = requests.get('https://test.instamojo.com/api/1.1/payment-requests/'+str(payid), headers=headers)    ### when in development
	json_ob = r.json()
	if (json_ob['success']):
		payment_request = json_ob['payment_request']
		purpose = payment_request['purpose']
		amount = payment_request['amount']
		amount = int(float(amount))
		try:
			group_id = int(purpose.split(' ')[1])
			payment_group = PaymentGroup.objects.get(id=group_id)
			count = payment_group.participant_set.all().count()
			if (amount/count) == 950:
				for part in payment_group.participant_set.all():
					part.controlz_paid = True
					part.paid = True
					part.save()
			elif (amount/count) == 650:
				for part in payment_group.participant_set.all():
					if part.paid:
						part.controlz_paid = True
						part.save()

			elif (amount/count) == 300:
				for part in payment_group.participant_set.all():
					part.paid = True
					part.save()

		except:		
			email = payment_request['email']
			print amount
			print type(amount)
			participant = Participant.objects.get(email=email)
			if amount == 950:
				participant.controlz_paid = True
			elif amount == 650.00 and participant.paid:
				participant.controlz_paid = True
			participant.paid = True
			participant.save()
		context = {
		'error_heading' : "Payment successful",
		'message':'Thank you for paying.',
		'url':request.build_absolute_uri(reverse('registrations:index'))
		}
		return render(request, 'registrations/message.html', context)
	
	else:

		payment_request = json_ob['payment_request']
		purpose = payment_request['purpose']
		email = payment_request['email']
		context = {
			'error_heading': "Payment error",
			'message': "An error was encountered while processing the payment. Please contact PCr, BITS, Pilani.",
			'url':request.build_absolute_uri(reverse('registrations:index'))
			}
		return render(request, 'registrations/message.html', context)

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