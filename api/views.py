from django.shortcuts import render
from registrations.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from registrations.models import *
from events.models import *
from registrations.views import *
from django.views.decorators.csrf import csrf_exempt
import sendgrid
import os
from sendgrid.helpers.mail import *
from registrations.sg_config import *

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status

import string
from random import sample, choice
chars = string.letters + string.digits

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def index(request):
	participant = Participant.objects.get(user=request.user)
	self_serializer = ParticipantSerializer(g_leader)
	if participant.is_cr:
		part_serializer = ParticipantSerializer(Participant.objects.filter(college=participant.college).exclude(participant), many=True)

	return Response({'user':unicode(request.user), 'participant':self_serializer.data, 'participants':part_serializer.data})

@api_view(['POST', 'GET'])
@permission_classes((AllowAny, ))
def create_user(request):

	part_serializer = ParticipantSerializer(data=request.data)
	try:
		Participant.objects.get(email=data['email'])
		return Response({'message':'Email has already registered.'})
	except:
		pass
	if part_serializer.is_valid():

		participant = part_serializer.save()
		send_to = request.data['email']
		name = request.data['name']
		body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
		<center><img src="http://bits-bosm.org/2016/static/docs/email_header.jpg"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 32nd edition of BITS Open Sports Meet (BOSM), the annual national sports meet of Birla Institute of Technology & Science, Pilani, India. This year, BOSM will be held from September 15th to 19th.             

Kindly go through the invite attached with this email and apply through our website www.bits-bosm.org. Applications close on 31st August 2016 at 1700 hrs.            

Please apply as soon as possible to enable us to confirm your participation at the earliest.             

We would be really happy to see your college represented at our sports festival.            

We look forward to seeing you at BOSM 2016.

<a href='%s'>Click Here</a> to verify your email.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT BOSM 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
CoSSAcn (Head)
Dept. of Publications & Correspondence, BOSM 2017
BITS Pilani
+91-7240105158, +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778
pcr@bits-bosm.org
</pre>
			'''%(name, str(request.build_absolute_uri(reverse("registrations:index"))) + 'email_confirm/' + generate_email_token(Participant.objects.get(email=send_to)) + '/')
		sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
		from_email = Email('register@bits-oasis.org')
		to_email = Email(send_to)
		subject = "Registration for OASIS '17"
		content = Content('text/html', body)

		try:
			mail = Mail(from_email, subject, to_email, content)
			response = sg.client.mail.send.post(request_body=mail.get())
		except :
			participant.delete()
			return Response({'message':'Email sending failed. Please try again.'})

		message = "A confirmation link has been sent to %s. Kindly click on it to verify your email address.(Email may be present in the spams folder)." %(send_to)
		return Response({'message':message})
	else:
		return Response({'message':get_errors(part_serializer._errors)}, status=status.HTTP_400_BAD_REQUEST)

############ Get Errors #############
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(message='')
def get_errors(d):
	for k,v in d.iteritems():
		if isinstance(v, dict):
			get_errors.message += get_errors(v)
		else:
			return v[0]
	return get_errors.message

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def show_events(request):

	participant = Participant.objects.get(user=request.user)
	events = Event.objects.all()
	events_added = [participation.event for participation in Participation.objects.filter(participant=participant)]
	events_left = [event for event in events if event not in events_added]
	added_serializer = EventSerializer(sports_added, many=True)
	left_serializer = EventSerializer(sports_left, many=True)

	return Response({'events_added':events_added.data, 'events_left':left_serializer.data,})

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def manage_events(request):

	data = request.data
	print data
	participant = Participant.objects.get(user=request.user)
	try:
		events_added = data['eventsadded']
		for e_id in eval(events_added):
			print e_id
			event = get_object_or_404(Event, id=int(e_id))
			part, created = Participation.objects.get_or_create(participant=participant, event=event)
	except KeyError:
		pass
		
	try:
		events_left = data['eventsleft']

		for e_id in eval(events_left):
			event = get_object_or_404(Event, id=int(e_id))
			try:
				Participation.objects.get(g_l=g_l, event=event).delete()
			except:
				continue
	except KeyError:
		pass
	
	participant = Participant.objects.get(user=request.user)
	events = Event.objects.all()
	events_added = [participation.event for participation in Participation.objects.filter(participant=participant)]
	events_left = [event for event in events if event not in events_added]
	added_serializer = EventSerializer(sports_added, many=True)
	left_serializer = EventSerializer(sports_left, many=True)

	return Response({'events_added':events_added.data, 'events_left':left_serializer.data,})

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_id(request):
	participant = Participant.objects.get(user=request.user)
	participant_serializer = ParticipantSerializer(gl)
	return Response(participant_serializer.data)

# @api_view(['POST', ])
# @permission_classes((IsAuthenticated, ))
# def cr_list(request):
# 	return HttpResponseRedirect('/')

# 	approved_list = Participation.objects.filter(participant__college=participant.college, cr_approved=True)
# 	disapproved_list = Participation.objects.filter(participant__college=participant.college, cr_approved=False)
# 	approved_serializer = ParticipantSerializer()

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def cr_approval(request):
	participant = Participant.objects.get(user=request.user)
	if not participant.is_cr:
		return Response({'message':'You do not have access to this.'})
	data = request.data
	try:
		id_list = eval(data['id_list'])
	except:
		return Response({'message':'Please select participants.'})
	for p_id in id_list:
		participation = Participation.objects.get(id=p_id, participant__college=participant.college)
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
			subject = 'Registration for OASIS \'17 REALM OF FICTION'
			content = Content('text/html', body)
			try:
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())
			except:
				appr_participant.user = None
				appr_participant.save()
				user.delete()
				return Response({'message':'Error encountered! Please try again.'})
	return Response({'message':'Login credentials sent to the respective participants.'})

@api_view(['POST', ])
@permission_classes((IsAuthenticated, ))
def cr_disapprove(request):
	participant = Participant.objects.get(user=request.user)
	if not participant.is_cr:
		return Response({'message':'You do not have access to this.'})
	data = request.data
	try:
		id_list = eval(data['id_list'])
	except:
		return Response({'message':'Please select participants.'})
	for p_id in id_list:
		participation = Participation.objects.get(id=p_id, participant__college=participant.college)
		participation.cr_approved = False
		participation.save()
	return Response({'message':'Successfully disapproved.'})

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_profile(request):
	participant = Participant.objects.get(user=request.user)
	participation_serializer = ParticipationSerializer(Participation.objects.filter(participant=participant, many=True))
	participant_serializer = ParticipantSerializer(participant, context={'request':request})
	return Response({'participant':participant_serializer.data, 'participations':participation_serializer.data})

@api_view(['POST', ])
@permission_classes((IsAuthenticated, ))
def edit_profile(request):
	participant = Participant.objects.get(user=request.user)
	data = request.data
	participant.name = data['name']
	participant.phone = data['phone']
	participant.save()
	participation_serializer = ParticipationSerializer(Participation.objects.filter(participant=participant, many=True))
	participant_serializer = ParticipantSerializer(participant, context={'request':request})
	return Response({'participant':participant_serializer.data, 'participations':participation_serializer.data})