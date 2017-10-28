from django.shortcuts import render
from registrations.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from registrations.models import *
from events.models import *
from messportal.models import *
from registrations.views import *
from django.views.decorators.csrf import csrf_exempt
import sendgrid
import os
from sendgrid.helpers.mail import *
from oasis2017.keyconfig import *
import re
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from ems.models import *
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
	print request.data
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

We look forward to seeing you at OASIS 2017.

<a href='%s'>Click Here</a> to verify your email.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT OASIS 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

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

@api_view(['POST',])
@permission_classes((AllowAny,))
def get_profile_bitsian(request):
	from oasis2017.keyconfig import bits_uuid
	if request.method == 'POST':
		data = request.data
		try:
			key = data['unique_key']
		except:
			return Response({'message':'It\'s not so easy, my friend. Nice thought though.'})
		if not key == bits_uuid:
			return Response({'message':'It\'s not so easy, my friend. Nice thought though.'})
		email = data['email']
		try:
			bitsian = Bitsian.objects.filter(email=email)[0]
			bitsian_serializer = BitsianSerializer(bitsian)
		except:
			return Response({'message':'Bitsian not found.'})
		profshow_serializer = AttendanceSerializer(Attendance.objects.filter(bitsian=bitsian), many=True)
		return Response({'bitsian':bitsian_serializer.data, 'prof_shows':profshow_serializer.data})

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_profile(request):
	participant = Participant.objects.get(user=request.user)
	if not participant.firewallz_passed:
		return Response({'message':'Register at Firewallz first.'})
	event_set = [participation.event for participation in Participation.objects.filter(participant=participant, pcr_approved=True)]
	event_serializer = EventSerializer(event_set, many=True)
	participant_serializer = ProfileSerializer(participant, context={'request':request})
	profshow_serializer = AttendanceSerializer(Attendance.objects.filter(participant=participant), many=True)
	return Response({'participant':participant_serializer.data, 'participations':event_serializer.data, 'prof_shows':profshow_serializer.data})

@api_view(['GET',])
@permission_classes((AllowAny, ))
def prof_show_part(request, part_barcode):
	participant = get_object_or_404(Participant, barcode=part_barcode)
	profshow_serializer = AttendanceSerializer(Attendance.objects.filter(participant=participant), many=True)
	return Response({'prof_shows':profshow_serializer.data})

@api_view(['POST', ])
@permission_classes((IsAuthenticated, ))
def edit_profile(request):
	participant = Participant.objects.get(user=request.user)
	if not participant.firewallz_passed:
		return Response({'message':'Register at Firewallz first.'})
	data = request.data
	participant.name = data['name']
	participant.phone = data['phone']
	participant.save()
	participation_serializer = ParticipationSerializer(Participation.objects.filter(participant=participant, many=True))
	participant_serializer = ParticipantSerializer(participant, context={'request':request})
	return Response({'participant':participant_serializer.data, 'participations':participation_serializer.data})

@api_view(['GET',])
@permission_classes((AllowAny,))
def all_events(request):
	event_serializer = BaseEventSerializer(Event.objects.all(), many=True)
	return Response(event_serializer.data)

@api_view(['GET',])
def all_prof_shows(request):
	user = request.user
	if user.is_superuser:
		prof_show_serializer = ProfShowSerializer(ProfShow.objects.all(), many=True)
		return Response(prof_show_serializer.data)
	clubdept = ClubDepartment.objects.get(user=user)
	# clubdept.profshows.all()
	prof_show_serializer = ProfShowSerializer(clubdept.profshows.all(), many=True)
	return Response(prof_show_serializer.data)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_event(request, e_id):
	event_serializer = EventDetailSerializer(Event.objects.get(id=e_id))
	return Response(event_serializer.data)

@api_view(['POST',])
@permission_classes((IsAuthenticated, ))
def add_profshow(request):
	user = request.user
	if not user.is_staff:
		return Response({'message':'Invalid access'})
	if not user.is_superuser:
		if not (user.username == 'deptlive' or user.username == 'controls'):
			return Response({'message':'Invalid Access'})
	data = request.data
	try:
		prof_show = ProfShow.objects.get(id=data['prof_show'])
	except:
		return Response({'message':'Invalid Prof Show'})
	barcode = data['barcode']
	if re.match(r'[h,f]\d{6}', barcode):
		try:
			bitsian = Bitsian.objects.filter(ems_code=barcode)[0]
			bitsian_serializer = BitsianSerializer(bitsian)
		except:
			return Response({'message':'Please check barcode of Bitsian'})
		try:
			attendance = Attendance.objects.get(bitsian=bitsian, prof_show=prof_show)
			attendance.count += int(data['count'])
			attendance.save()
		except:
			attendance = Attendance()
			attendance.bitsian = bitsian
			attendance.prof_show = prof_show
			attendance.paid = True
			attendance.count = data['count']
			attendance.save()
		profshow_bill = BitsProfShowBill()
		profshow_bill.prof_show = prof_show
		profshow_bill.buyer_id = data['barcode']
		profshow_bill.quantity = data['count']
		profshow_bill.amount = prof_show.price*int(data['count'])
		profshow_bill.created_by = data['created_by']
		profshow_bill.save()
		attendance_serializer = AttendanceSerializer(attendance)
		return Response({'profshow':attendance_serializer.data, 'bitsian':bitsian_serializer.data})
	elif re.match(r'oasis17\w{8}', barcode):
		try:
			participant = Participant.objects.get(barcode=data['barcode'])
			participant_serializer = ParticipantSerializer(participant, context={'request':request})
		except:
			return Response({'message':'Please check barcode of Participant'})
		profshow_bill = ProfShowBill()
		try:
			bits_id = data['bits_id']
			if not bits_id == '':
				if not re.match(r'[h,f]\d{6}', bits_id):
					return Response({'message':'Invalid BITS Id'})
				profshow_bill.bits_id = bits_id
		except:
			pass
		try:
			attendance = Attendance.objects.get(participant=participant, prof_show=prof_show)
			attendance.count += int(data['count'])
			attendance.save()
		except:
			attendance = Attendance()
			attendance.participant = participant
			attendance.prof_show = prof_show
			attendance.paid = True
			attendance.count = data['count']
			attendance.save()
		profshow_bill.prof_show = prof_show
		profshow_bill.buyer_id = data['barcode']
		profshow_bill.quantity = data['count']
		profshow_bill.n2000 = int(data['n_2000'])
		profshow_bill.intake = 0
		profshow_bill.outtake = 0
		if data['n_2000']>0:
			profshow_bill.intake += int(data['n_2000'])*2000
		else:
			profshow_bill.outtake -= int(data['n_2000'])*2000
		profshow_bill.n500 = data['n_500']
		if data['n_500']>0:
			profshow_bill.intake += int(data['n_500'])*500
		else:
			profshow_bill.outtake -= int(data['n_500'])*500
		profshow_bill.n200 = data['n_200']
		if data['n_200']>0:
			profshow_bill.intake += int(data['n_200'])*200
		else:
			profshow_bill.outtake -= int(data['n_200'])*200
		profshow_bill.n100 = data['n_100']
		if data['n_100']>0:
			profshow_bill.intake += int(data['n_100'])*100
		else:
			profshow_bill.outtake -= int(data['n_100'])*100
		profshow_bill.n50 = data['n_50']
		if data['n_50']>0:
			profshow_bill.intake += int(data['n_50'])*50
		else:
			profshow_bill.outtake -= int(data['n_50'])*50
		profshow_bill.n20 = data['n_20']
		if data['n_20']>0:
			profshow_bill.intake += int(data['n_20'])*20
		else:
			profshow_bill.outtake -= int(data['n_20'])*20
		profshow_bill.n10 = data['n_10']
		if data['n_10']>0:
			profshow_bill.intake += int(data['n_10'])*10
		else:
			profshow_bill.outtake -= int(data['n_10'])*10
		profshow_bill.amount = profshow_bill.intake - profshow_bill.outtake
		profshow_bill.created_by = data['created_by']
		profshow_bill.save()
		attendance_serializer = AttendanceSerializer(attendance)
		return Response({'profshow':attendance_serializer.data, 'participant':participant_serializer.data})
	else:
		return Response({'message':'Please check barcode of Participant'})
	

@api_view(['POST',])
@permission_classes((IsAuthenticated, ))
def validate_profshow(request):
	user = request.user
	if not user.is_staff:
		return Response({'message':'Invalid access'})
	if not user.is_superuser:
		if not user.username == 'deptlive':
			return Response({'message':'Invalid Access'})
	data = request.data
	barcode = data['barcode']
	try:
		prof_show = ProfShow.objects.get(id=data['prof_show'])
	except:
		return Response({'message':'Invalid Prof Show'})
	if re.match(r'[h,f]\d{6}', barcode):
		try:
			bitsian = Bitsian.objects.filter(ems_code=barcode)[0]
			bitsian_serializer = BitsianSerializer(bitsian)
		except:
			return Response({'message':'Please check barcode of Bitsian'})
		try:
			attendance = Attendance.objects.get(bitsian=bitsian, prof_show=prof_show)
		except:
			return Response({'message':'No more passes left. Please register at DoLE Booth.'})
		if attendance.count > 0:
			attendance.count -= 1
			attendance.passed_count += 1
			attendance.save()
			return Response({'message':'Success. Passes Left = ' + str(attendance.count), 'bitsian':bitsian_serializer.data})
		else:
			return Response({'message':'No more passes left. Please register at DoLE Booth.'})
	elif re.match(r'oasis17\w{8}', barcode):
		try:
			participant = Participant.objects.get(barcode=data['barcode'])
			participant_serializer = ParticipantSerializer(participant, context={'request':request})
		except:
			return Response({'message':'Please check barcode of Participant'})
		try:
			attendance = Attendance.objects.get(participant=participant, prof_show=prof_show)
		except:
			return Response({'message':'No more passes left. Please register at DoLE Booth.'})
		if attendance.count > 0:
			attendance.count -= 1
			attendance.passed_count += 1
			attendance.save()
			return Response({'message':'Success. Passes Left = ' + str(attendance.count), 'participant':participant_serializer.data})
		else:
			return Response({'message':'No more passes left. Please register at DoLE Booth.'})
	else:
		return Response({'message':'Invalid code.'})

@api_view(['GET'])
def get_events_cd(request):
	user = request.user
	try:
		cd = ClubDepartment.objects.get(user=user)
		events = cd.events.all()
	except:
		if not user.is_superuser:
			return Response({'status':2, 'message':'You don\'t have access to this.' })
		events = Event.objects.all()
	event_serializer = BaseEventSerializer(events, many=True)
	return Response({'events':event_serializer.data})

@api_view(['POST'])
def register_team(request):
	data = request.data
	event = Event.objects.get(id=data['event_id'])
	user = request.user
	try:
		cd = ClubDepartment.objects.get(user=user)
		if not event in cd.events.all():
			raise Exception
	except:
		if not user.is_superuser:
			return Response({'status':2, 'message':'You don\'t have access to this.'})
	try:
		level = Level.objects.get(position=1, event=event)
	except:
		return Response({'status':3, 'message':'Levels not added'}) 
	team_str = data['team']
	team_ids = team_str.split(',')
	count=Team.objects.all().count()
	team = Team.objects.create(name='Team-'+str(count)+' ' + event.name, event=event)
	x=0
	for mem in team_ids:
		if re.match(r'oasis17\w{8}', mem):
			try:
				p = Participant.objects.get(barcode=mem)
			except:
				team.delete()
				return Response({'status':0, 'message':'Invalid Codes'})
			team.members.add(p)
			if x==0:
				team.leader = p
		elif re.match(r'[h,f]\d{6}', mem):
			try:
				b = Bitsian.objects.filter(ems_code=mem)[0]
			except:
				team.delete()
				return Response({'status':0, 'message':'Invalid Codes'})
			team.members_bitsian.add(b)
			if x==0:
				team.leader_bitsian = b
		else:
			team.delete()
			return Response({'status':0, 'message':'Invalid Codes'})
		x+=1
	team.save()
	level.teams.add(team)
	s = Score(team=team, level=level)
	s.save()
	return Response({'status':1, 'message':'Team added successfully.'})