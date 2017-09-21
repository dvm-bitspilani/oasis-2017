from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse
from models import *
from events.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
import sendgrid
import os
from sendgrid.helpers.mail import *
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo
import re
from preregistrations.instaconfig import *
from django.contrib.auth.models import User
import string
from random import sample, choice
chars = string.letters + string.digits

def index(request):
	if request.user.is_authenticated():
		user = request.user
		participant = Participant.objects.get(user=user)
		return render(request, 'registrations/profile.html', {'participant':participant,})
	else:
		if request.method == 'POST':
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					
					return HttpResponseRedirect(reverse('registrations:index'))
				else:
					context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional Contacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .'}
					return JsonResponse({'status':0, 'context':context})
			else:
				context = {'error_heading' : "Invalid Login Credentials", 'message' :  'Invalid Login Credentials. Please try again'}
				return JsonResponse({'status':0, 'context':context})

		else:
			return render(request, 'registrations/login.html')

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

def register(request):

	if request.method == 'POST':

		data = request.POST
		try:
			Participant.objects.get(email=data['email'])
			return JsonResponse({'status':0, 'message':'Email already registered.'})
		except:
			pass
		if len(data['events']) == 0:
			return JsonResponse({'status':0, 'message':'Select atleast one event'})
		else:
			participant = Participant()
			participant.name = data['name']
			participant.gender = data['gender']
			participant.city = data['city']
			participant.email = data['email']
			participant.college = College.objects.get(name=data['college'])
			participant.phone = data['phone']
			participant.head_of_society = data['head_of_society']
			participant.year_of_study = data['year_of_study']
			participant.save()
			for key in events:
				event = Event.objects.get(id=int(key))
				Participation.objects.create(event=event, participant=participant)
			participant.save()


			send_to = request.POST["email"]
			name = request.POST["name"]
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

<a href='%s'>Click Here</a> to verify your email.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT BOSM 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
CoSSAcn (Head)
Dept. of Publications & Correspondence, BOSM 2017
BITS Pilani
+91-9929022741
pcr@bits-bosm.org
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

			try:
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())
			except :
				participant.delete()
				return JsonResponse({'status':0, 'message':'Error sending email. Please try again.'})

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

################################# End of helper functions ###############################

def email_confirm(request):
	member = authenticate_email_token(token)
	
	if member:
		context = {
			'error_heading': 1,
			'message': 'Your email has been verified. Please wait for further correspondence from the Department of PCr, BITS, Pilani',
		}
	else:
		context = {
			'status': 0,
			'error_heading': "Invalid Token",
			'message': "Sorry! This is an invalid token. Email couldn't be verified. Please try again.",
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
			'''%(name, username, password)
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
def participant_payment(request, p_id):
	participant = get_object_or_404(Participant, id=p_id)
	name = participant.name
	email = participant.email
	phone = participant.phone
	purpose = 'Payment for OASIS \'17'
	response = api.payment_request_create(buyer_name= name,
						email= email,
						phone= number,
						amount = 950,
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
	if request.method == 'POST':
		user = request.user
		participant = Participant.object.get(user=user)
		if not participant.is_cr:
			context = {
			'status': 0,
			'error_heading': "Invalid Access",
			'message': "Sorry! You are not an approved college representative.",
			}
			return render(request, 'registrations/message.html', context)
		data = request.POST
		part_list = Participant.objects.filter(id__in=data.getlist('part_list'))
		group = PaymentGroup()
		group.amount_paid = 950*len(part_list)
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
				'message': "An error was encountered while processing the request. Please contact PCr, BITS, Pilani.",
				}
			return render(request, 'registrations/message.html')

	else:
		participant_list = Participant.objects.filter(college=participant.college, pcr_approved=True)
		return render(request, 'cr_payment.html', {'participant_list':participant_list})

@login_required
def upload_docs(request):
	participant = Participant.object.get(user=request.user)
	if request.method == 'POST':
		try:
			imageform = ImageUploadForm(request.POST, request.FILES)
			image = participant.profile_pic
			if image is not None:
				image.delete(save=True)
			if imageform.is_valid():
				imageform.save()
			else:
				context = {
				'status': 0,
				'error_heading': "Error",
				'message': "Sorry! Some errors were encountered while uploading the image. Please try again.",
				}
				return render(request, 'registrations/message.html', context)
		except:
			pass
		
		try:
			docform = DocUploadForm(request.POST, request.FILES)
			docs = participant.verify_docs
			if docs is not None:
				docs.delete(save=True)
			if docform.is_valid():
				docform.save()
			else:
				context = {
				'status': 0,
				'error_heading': "Error",
				'message': "Sorry! Some errors were encountered while uploading the documents. Please try again.",
				}
				return render(request, 'registrations/message.html', context)
		except:
			pass
	return render(request, 'registrations/upload_form.html', {'participant':participant})

def apirequest(request):
	import requests
	payid=str(request.GET['payment_request_id'])
	headers = {'X-Api-Key': API_KEY,
    	       'X-Auth-Token': AUTH_TOKEN}
	
   	r = requests.get('https://www.instamojo.com/api/1.1/payment-requests/'+str(payid),
              	 headers=headers)
	#r = requests.get('https://test.instamojo.com/api/1.1/payment-requests/'+str(payid), headers=headers)    ### when in development
	json_ob = r.json()
	if (json_ob['success']):
		payment_request = json_ob['payment_request']
		purpose = payment_request['purpose']
		try:
			group_id = int(purpose.split(' ')[1])
			payment_group = PaymentGroup.objects.get(id=group_id)
			for part in payment_group.participant_set.all():
				part.paid = True
				part.save()

		except:		
			email = payment_request['email']
			participant = Participant.objects.get(email=email)
			participant.paid = True
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