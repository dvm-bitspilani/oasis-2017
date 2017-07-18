from django.shortcuts import render
from django.http import JsonResponse
from models import IntroReg, College
from events.models import Event
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

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
	college_list = College.objects.all()
	event_list = Event.objects.all()
	return JsonResponse({'college_list':college_list, 'event_list':event_list})