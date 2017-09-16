from django.shortcuts import render
from django.http import JsonResponse
from models import *
from events.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .forms import *

def index(request):

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

		uform = UserForm(data=request.POST)
		pform = GroupLeaderForm(data=request.POST)

		if uform.is_valid() and pform.is_valid():

			user = uform.save()
			user.set_password(user.password)
			user.is_active = False
			user.save()
			g_l_profile = pform.save(commit=False)
			g_l_profile.user = user
			g_l_profile.save()

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
			'''%(name, str(request.build_absolute_uri(reverse("registrations:index"))) + 'email_confirm/' + generate_email_token(GroupLeader.objects.get(email=send_to)) + '/')

			# email = EmailMultiAlternatives("Registration for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("registrations:email_confirm", kwargs={'token':generate_email_token(GroupLeader.objects.get(email=send_to))})))  + '/' + ' to confirm.', 
			# 								'register@bits-bosm.org', [send_to.strip()]
			# 								)
			# email.attach_alternative(body, "text/html")
			sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
			from_email = Email('register@bits-bosm.org')
			to_email = Email(send_to)
			subject = "Registration for BOSM '17"
			content = Content('text/html', body)

			try:
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())
			except :
				return render(request, 'registrations/message.html', {'message':"Mail not sent. Please try again"})
				user.delete()


			message = "A confirmation link has been sent to %s. Kindly click on it to verify your email address." %(send_to)
			return render(request, 'registrations/message.html', {'message':message})

		else:

			message = str(uform.errors) + str(pform.errors)
			return render(request, 'registrations/message.html', {'message':message, 'url':request.META.get('HTTP_REFERER')})				

	else:

		uform = UserForm()
		pform = GroupLeaderForm()

		return render(request, 'registrations/signup.html', {'uform':uform, 'pform':pform})	


############# Helper functions for Django Email ##########

def generate_email_token(gleader):

	import uuid
	token = uuid.uuid4().hex
	registered_tokens = [profile.email_token for profile in GroupLeader.objects.all()]

	while token in registered_tokens:
		token = uuid.uuid4().hex

	gleader.email_token = token
	gleader.save()
	
	return token

def authenticate_email_token(token):

	try:
		gleader = GroupLeader.objects.get(email_token=token)
		gleader.email_verified = True
		gleader.email_token = None
		gleader.save()

		return gleader

	except :

		return False

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

def register(request):
	college_list_json = serializers.serialize("json", College.objects.all())
	event_list_json = serializers.serialize("json", Event.objects.all())
	return JsonResponse({'college_list':college_list_json, 'event_list':event_list_json})