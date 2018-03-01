from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect, Http404
from models import Rocktaves, StandUp, StreetDance, PitchPerfect, RapWars
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from instamojo_wrapper import Instamojo
import re
from oasis2017.keyconfig import *

try:
	from oasis2017.config import *
	api = Instamojo(api_key=INSTA_API_KEY, auth_token=AUTH_TOKEN)
except:
	api = Instamojo(api_key=INSTA_API_KEY_test, auth_token=AUTH_TOKEN_test, endpoint='https://test.instamojo.com/api/1.1/') #when in development

@csrf_exempt
def index(request):

	if request.method == 'POST':

		

		event_id = request.POST['form_id']


		########## Rocktaves ##########
		if int(event_id) == 0:

			email = request.POST['email'].replace('%40','@')

			if Rocktaves.objects.filter(email_address = email):
				return JsonResponse({'status':0})

			mobile_number = request.POST['phone']

			if len(mobile_number) == 10:
				try:

					number = int(mobile_number)

					rocktaves = Rocktaves()
					rocktaves.name = request.POST['name']
					rocktaves.city = request.POST['city']
						
					if request.POST['gender'] == 'M':
						rocktaves.gender = 'Male'
					elif request.POST['gender'] == 'F':
						rocktaves.gender = 'Female'

					rocktaves.phone = '+91' + mobile_number
					rocktaves.email_address = email
					rocktaves.save()
					name = request.POST['name']
					data = {'status':1,'email':email, 'name':name, 'Event':'Rocktaves'}
						
					return JsonResponse(data)

				except ValueError:
					data = {'status':2}
					return JsonResponse(data)

			else:
				data = {'status':2}
				return JsonResponse(data)


		########## PitchPerfect ##########

		if int(event_id) == 1:

			g_l = request.POST['group_lead']

			g_m = request.POST['group_memb']
			email = request.POST['email'].replace('%40','@')

			user = PitchPerfect.objects.filter(email_address = email)
			if user:
				if user[0].paid:
					return JsonResponse({'status':0})
				else: 
					user.delete()




			mobile_number = request.POST['phone']
			# email = request.POST['email'].replace('%40','@')

			if len(mobile_number) == 10:
				try:

					number = int(mobile_number)

					

					number_of_members = int(request.POST['number_of_members'])
					pitch_perfect = PitchPerfect()
					pitch_perfect.g_leader = g_l
					pitch_perfect.members = g_m
					pitch_perfect.city = request.POST['city']
					pitch_perfect.college = request.POST['college']
					pitch_perfect.phone = '+91' + mobile_number
					pitch_perfect.email_address = email
					pitch_perfect.number_of_members = number_of_members
					pitch_perfect.save()
					name = g_l
					#data = {'status':1,'email':email, 'name':name, 'Event':'Pitch Perfect'}
					
					response = api.payment_request_create(buyer_name= g_l,
						email= email,
						phone= number,
						amount = 300*(number_of_members+1),
						purpose="Pitch Perfect",
						redirect_url= request.build_absolute_uri(reverse("API Request"))
						)
					print  email	, response['payment_request']['longurl']			
					data = {'status':5,
					'url': response['payment_request']['longurl'] 
					}
					return JsonResponse(data)

				except ValueError:
					data = {'status':2}
					return JsonResponse(data)

			else:
				data = {'status':2}
				return JsonResponse(data)



		########## RapWars ##########


		if int(event_id) == 2:

			email = request.POST['email'].replace('%40','@')
			
			user = RapWars.objects.filter(email_address = email)
			if user:
				if user[0].paid:
					return JsonResponse({'status':0})
				else :
					user.delete()
			mobile_number = request.POST['phone']

			if len(mobile_number) == 10:
				try:

					number = int(mobile_number)
					rapwars = RapWars()
					rapwars.name = request.POST['name']
					rapwars.city = request.POST['city']
						
					if request.POST['gender'] == 'M':
						rapwars.gender = 'Male'
					elif request.POST['gender'] == 'F':
						rapwars.gender = 'Female'

					rapwars.phone = '+91' + mobile_number
					rapwars.email_address = email
					rapwars.save()
					name = request.POST['name']
					response = api.payment_request_create(buyer_name= name,
						email= email,
						phone= number,
						amount = 300,
						purpose="RapWars",
						redirect_url= request.build_absolute_uri(reverse("API Request"))
						)
					print  email	, response['payment_request']['longurl']			
					data = {'status':5,
					'url': response['payment_request']['longurl'] 
					}
					return JsonResponse(data)
				except ValueError:
					data = {'status':2}
					return JsonResponse(data)

			else:
				data = {'status':2}
				return JsonResponse(data)


		########## Street Dance ##########		


		if int(event_id) == 3:

			
			g_l = request.POST['group_lead']

			g_m = request.POST['group_memb']
			

			email = request.POST['email'].replace('%40','@')

			user = StreetDance.objects.filter(email_address = email)
			if user:
				if user[0].paid:
					return JsonResponse({'status':0})
				else:
					user.delete()
			mobile_number = request.POST['phone']

			if len(mobile_number) == 10:
				try:

					number = int(mobile_number)
					
					number_of_members = int(request.POST['number_of_members'])
					street_dance = StreetDance()
					street_dance.g_leader = g_l
					street_dance.members = g_m
					street_dance.city = request.POST['city']
					street_dance.college = request.POST['college']
					street_dance.phone = '+91' + mobile_number
					street_dance.email_address = email
					street_dance.number_of_members = number_of_members
					street_dance.save()
					name = g_l
					data = {'status':1,'email':email, 'name':name, 'Event':'Street Dance'}
					
					response = api.payment_request_create(
						buyer_name= g_l,
						email = email,
						phone = number,
						amount = 300*(number_of_members+1),
						purpose = "Street Dance",
						redirect_url = request.build_absolute_uri(reverse("API Request"))
						)
					data={'status':5,
						'url':response['payment_request']['longurl']
						}
					return JsonResponse(data)

					

				except ValueError:
					data = {'status':2}
					return JsonResponse(data)

			else:
				data = {'status':2}
				return JsonResponse(data)



		########## Humor Fest ##########		


		if int(event_id) == 4:
		
			email = request.POST['email'].replace('%40','@')

			if StandUp.objects.filter(email_address = email):

				return JsonResponse({'status':0})

			mobile_number = request.POST['phone']

			if len(mobile_number) == 10:
				try:

					number = int(mobile_number)

					standup = StandUp()
					standup.name = request.POST['name']
					standup.city = request.POST['city']
						
					if request.POST['gender'] == 'M':
						standup.gender = 'Male'
					elif request.POST['gender'] == 'F':
						standup.gender = 'Female'

					standup.phone = '+91' + mobile_number
					standup.email_address = email
					standup.save()
					name = request.POST['name']
					data = {'status':1,'email':email, 'name':name, 'Event':'StandUp SoapBox'}
					
					return JsonResponse(data)

					
				except ValueError:
					data = {'status':2}
					return JsonResponse(data)

			else:
				data = {'status':2}
				return JsonResponse(data)


	return render(request, 'preregistrations/index.html')

def apirequest(request):

	import requests
	payid=str(request.GET['payment_request_id'])
	headers = {'X-Api-Key': API_KEY,
    	       'X-Auth-Token': AUTH_TOKEN}
	
   	r = requests.get('https://www.instamojo.com/api/1.1/payment-requests/'+str(payid),headers=headers)
	# r = requests.get('https://test.instamojo.com/api/1.1/payment-requests/'+str(payid),headers=headers)    
    ### when in development
	json_ob = r.json()
	print json_ob
	if (json_ob['success']):
		payment_request = json_ob['payment_request']
		purpose = payment_request['purpose']
		email = payment_request['email']

		if "Pitch" in purpose:

			pitch_perfect = PitchPerfect.objects.get(email_address=email)
			pitch_perfect.paid = True
			pitch_perfect.save()

		if "Street" in purpose:

			street_dance = StreetDance.objects.get(email_address=email)
			street_dance.paid = True	
			street_dance.save()

		if "Rap" in purpose:

			rap_wars = RapWars.objects.get(email_address=email)
			rap_wars.paid = True
			rap_wars.save()

		return render(request, 'preregistrations/index.html', {'message':'Payment Successful'})
	else:
		return render(request, 'preregistrations/index.html', {'message':'Payment unSuccessful'}) 


@staff_member_required
def get_excel_sheet(request, event):
	from django.http import HttpResponse, HttpResponseRedirect
	import xlsxwriter
	from models import StandUp, StreetDance, PitchPerfect, Rocktaves, RapWars
	# if request.POST:
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
	
	if re.match(event, 'StandUp'):

		stand = StandUp.objects.order_by('email_address')
		su_list = [{'obj': i} for i in stand]
		if su_list:
			worksheet.write(x, 0, "StandUp Soapbox")
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
				worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_address', 'NA'))
			x+=len(su_list)+2

	elif re.match(event, 'StreetDance'):
		street = StreetDance.objects.filter(paid=True).order_by('email_address')
		sd_list = [{'obj': i} for i in street]
		if sd_list:
			worksheet.write(x, 0, "Street Dance")
			x+=1
			worksheet.write(x, 0, "S.No.")		
			worksheet.write(x, 1, "Group Leader")
			worksheet.write(x, 2, "City")
			worksheet.write(x, 3, "College")
			worksheet.write(x, 4, "Phone No.")
			worksheet.write(x, 5, "Email ID")
			worksheet.write(x, 6, "Members")
			x+=1
			for i, row in enumerate(sd_list):
				worksheet.write(i+x, 0, i)
				worksheet.write(i+x, 1, deepgetattr(row['obj'], 'g_leader', 'NA'))
				worksheet.write(i+x, 2, deepgetattr(row['obj'], 'city', 'NA'))
				worksheet.write(i+x, 3, deepgetattr(row['obj'], 'college', 'NA'))
				worksheet.write(i+x, 4, deepgetattr(row['obj'], 'phone', 'NA'))
				worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_address', 'NA'))
				worksheet.write(i+x, 6, deepgetattr(row['obj'], 'members', 'NA'))
			x+=len(sd_list)+2


	elif re.match(event, 'PitchPerfect'):

		pitch = PitchPerfect.objects.filter(paid=True).order_by('email_address')
		pp_list = [{'obj': i} for i in pitch]
		if pp_list:
			worksheet.write(x, 0, "Pitch Perfect")
			x+=1
			worksheet.write(x, 0, "S.No.")		
			worksheet.write(x, 1, "Group Leader")
			worksheet.write(x, 2, "City")
			worksheet.write(x, 3, "College")
			worksheet.write(x, 4, "Phone No.")
			worksheet.write(x, 5, "Email ID")
			worksheet.write(x, 6, "Members")
			x+=1
			for i, row in enumerate(pp_list):
				worksheet.write(i+x, 0, i)
				worksheet.write(i+x, 1, deepgetattr(row['obj'], 'g_leader', 'NA'))
				worksheet.write(i+x, 2, deepgetattr(row['obj'], 'city', 'NA'))
				worksheet.write(i+x, 3, deepgetattr(row['obj'], 'college', 'NA'))
				worksheet.write(i+x, 4, deepgetattr(row['obj'], 'phone', 'NA'))
				worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_address', 'NA'))
				worksheet.write(i+x, 6, deepgetattr(row['obj'], 'members', 'NA'))
	
			x+=len(pp_list)+2

	
	elif re.match(event, 'Rocktaves'):

		rock = Rocktaves.objects.order_by('email_address')
		ro_list = [{'obj': i} for i in rock]
		if ro_list:
			worksheet.write(x, 0, "Rocktaves")
			x+=1
			worksheet.write(x, 0, "S.No.")
			worksheet.write(x, 1, "Name")
			worksheet.write(x, 2, "City")
			worksheet.write(x, 3, "Phone No.")
			worksheet.write(x, 4, "Gender")
			worksheet.write(x, 5, "Email ID")
			x+=1
			for i, row in enumerate(ro_list):
				worksheet.write(i+x, 0, i)			
				worksheet.write(i+x, 1, deepgetattr(row['obj'], 'name', 'NA'))
				worksheet.write(i+x, 2, deepgetattr(row['obj'], 'city', 'NA'))
				worksheet.write(i+x, 3, deepgetattr(row['obj'], 'phone', 'NA'))
				worksheet.write(i+x, 4, deepgetattr(row['obj'], 'gender', 'NA'))
				worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_address', 'NA'))
			x+=len(ro_list)+2	

	
	elif re.match(event, 'RapWars'):

		rap = RapWars.objects.filter(paid=True).order_by('email_address')
		rw_list = [{'obj': i} for i in rap]
		if rw_list:
			worksheet.write(x, 0, "Rap Wars")
			x+=1
			worksheet.write(x, 0, "S.No.")
			worksheet.write(x, 1, "Name")
			worksheet.write(x, 2, "City")
			worksheet.write(x, 3, "Phone No.")
			worksheet.write(x, 4, "Gender")
			worksheet.write(x, 5, "Email ID")
			x+=1
			for i, row in enumerate(rw_list):
				worksheet.write(i+x, 0, i)			
				worksheet.write(i+x, 1, deepgetattr(row['obj'], 'name', 'NA'))
				worksheet.write(i+x, 2, deepgetattr(row['obj'], 'city', 'NA'))
				worksheet.write(i+x, 3, deepgetattr(row['obj'], 'phone', 'NA'))
				worksheet.write(i+x, 4, deepgetattr(row['obj'], 'gender', 'NA'))
				worksheet.write(i+x, 5, deepgetattr(row['obj'], 'email_address', 'NA'))
			x+=len(rw_list)+2



	else:

		raise Http404("Event name not among : StandUp, Rocktaves, RapWars, StreetDance, PitchPerfect")


	workbook.close()
	filename = 'ExcelReport' + event + '.xlsx'
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