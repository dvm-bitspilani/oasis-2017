from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from registrations.models import *
from .models import *
from events.models import *
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from functools import reduce
from registrations.urls import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from oasis2017.settings import BASE_DIR
import os
from time import gmtime, strftime
import string
from pcradmin.views import get_cr_name, gen_barcode, get_pcr_number
from django.contrib import messages
from django.contrib.auth.models import User
import sendgrid
import os
import re   
from sendgrid.helpers.mail import *
from oasis2017.keyconfig import *
import string
from random import sample, choice
from django.contrib import messages
chars = string.letters + string.digits

############################### Helper Function ########################################################

def get_group_leader(group):
    return group.participant_set.get(is_g_leader=True)

def get_event_string(participant):
    participation_set = Participation.objects.filter(participant=participant, pcr_approved=True)
    events = ''
    for participation in participation_set:
        events += participation.event.name + ', '
    events = events[:-2]
    return events

def generate_group_code(group):
	group_id = group.id
	encoded = group.group_code
	if encoded == '':
		raise ValueError
	if encoded is not None:
		return encoded
	group_ida = "%04d" % int(group_id)
	college_code = ''.join(get_group_leader(group).college.name.split(' '))
	if len(college_code)<4:
		college_code += str(0)*(4-len(college_code))
	group.group_code = college_code + group_ida
	group.save()
	return encoded

def generate_ckgroup_code(group):
	group_id = group.id
	encoded = group.group_code
	if encoded == '':
		raise ValueError
	if encoded is not None:
		return encoded
	group_ida = "%04d" % int(group_id)
	college_code = ''.join(group.participant_set.all()[0].college.name.split(' '))
	if len(college_code)<4:
		college_code += str(0)*(4-len(college_code))
	group.group_code = college_code + group_ida
	group.save()
	return encoded

########################################### End Of Helper Functions ##############################################################
@staff_member_required
def index(request):
	if request.user.username.lower() == 'controls':
		return redirect(reverse('regsoft:controls_home'))
	if request.user.username.lower() == 'recnacc':
		return redirect(reverse('regsoft:recnacc_home'))
	if request.user.username == 'firewallz' or request.user.is_superuser:
		return redirect(reverse('regsoft:firewallz_home'))

########################################### Firewallz coz they're pretty sweet people ############################################

@staff_member_required
def firewallz_home(request):
    college_list = [college for college in College.objects.all() if college.participant_set.filter(is_cr=True)]
    print college_list
    rows = [{'data':[college.name, college.participant_set.get(college=college, is_cr=True).name,college.participant_set.filter(pcr_final=True).count(), college.participant_set.filter(pcr_final=True, firewallz_passed=True).count()],'link':[{'url':request.build_absolute_uri(reverse('regsoft:firewallz_approval', kwargs={'c_id':college.id})), 'title':'Approve Participants'},]} for college in college_list]
    headings = ['College', 'CR', 'PCr Finalised Participants', 'Firewallz Passed','Approve Participants']
    title = 'Select college to approve Participants'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def firewallz_approval(request, c_id):
    college = get_object_or_404(College, id=c_id)
    if request.method == 'POST':
        try:
            data = request.POST
            id_list = data.getlist('id_list')
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        try:
            g_leader_id = data['g_leader_id']
            if not g_leader_id in id_list:
                messages.warning(request,'Please select a Group Leader from the participant list.')
                return redirect(request.META.get('HTTP_REFERER'))   
            g_leader = Participant.objects.get(id=g_leader_id)
            g_leader.is_g_leader = True
            g_leader.save()
        
        except:
            messages.warning(request,'Please select a Group Leader.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        group = Group.objects.create()
        for part_id in id_list:
            part = Participant.objects.get(id=part_id)
            if part.group is not None:
                g_leader.is_g_leader = False
                g_leader.save()
                group.delete()
                context = {
                    'error_heading': "Error",
                    'message': "Participant(s) already in a group",
                    'url':request.build_absolute_uri(reverse('regsoft:firewallz_home'))
                    }
                return render(request, 'registrations/message.html', context)
            part.firewallz_passed=True
            part.group = group
            part.save() 
        encoded = generate_group_code(group)
        group.save()
        part_list = Participant.objects.filter(id__in=id_list)
        return redirect(reverse('regsoft:get_group_list', kwargs={'g_id':group.id}))
        # url = request.build_absolute_uri(reverse('registrations:generate_qr'))
        # return render(request, 'regsoft/card.html', {'part_list':part_list,'url':url})
    
    groups_passed = [group for group in Group.objects.all() if get_group_leader(group).college == college]
    unapproved_list = college.participant_set.filter(pcr_final=True, firewallz_passed=False, is_guest=False)
    print groups_passed
    return render(request, 'regsoft/firewallz_approval.html', {'groups_passed':groups_passed, 'unapproved_list':unapproved_list, 'college':college})

@staff_member_required
def add_guest(request):
    if request.method == 'POST':
        data = request.POST
        email = data['email']
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            messages.warning(request,'Please enter a valid email address.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            try:
                Participant.objects.get(email=data['email'])
                messages.warning(request,'Email already registered.')
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                pass
            participant = Participant()
            participant.name = str(data['name'])
            participant.gender = str(data['gender'])
            participant.city = str(data['city'])
            participant.email = str(data['email'])
            participant.college = College.objects.get(name=str(data['college']))
            participant.phone = int(data['phone'])
            participant.is_guest = True
            participant.email_verified = True
            try:
                participant.bits_id = str(data['bits_id'])
            except:
                messages.warning(request, 'Please enter the bits id')
                return redirect(request.META.get('HTTP_REFERER'))
            participant.firewallz_passed = True
            participant.save()
            ems_code = str(participant.college.id).rjust(3,'0') + str(participant.id).rjust(4,'0')
            participant.ems_code = ems_code
            encoded = gen_barcode(participant)
            participant.save()
            username = participant.name.split(' ')[0] + str(participant.id)
            password = ''.join(choice(chars) for _ in xrange(8))
            user = User.objects.create_user(username=username, password=password)
            participant.user = user
            participant.save()

            send_to = participant.email
            name = participant.name
            body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
			<center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 47th edition of OASIS, the annual cultural fest of Birla Institute of Technology & Science, Pilani, India. This year, OASIS will be held from October 31st to November 4th.             
           
This is to inform you that your guest registration is complete.
You can now login in the app using the following credentials and get your exclusive qrcode:
username : '%s'
password : '%s'

Regards,
StuCCAn (Head)
Dept. of Publications & Correspondence, OASIS 2017
BITS Pilani
%s
pcr@bits-oasis.org
</pre>
			''' %(name, username, password, get_pcr_number())
            sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
            from_email = Email('register@bits-oasis.org')
            to_email = Email(send_to)
            subject = "Registration for OASIS '17 REALMS OF FICTION"
            content = Content('text/html', body)

            try:
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
            except :
                participant.user = None
                participant.save()
                user.delete()
                participant.delete()
                context = {
                    'url':request.build_absolute_uri(reverse('regsoft:firewallz_home')),
                    'error_heading': "Error sending mail",
                    'message': "Sorry! Error in sending email. Please try again.",
                }
                return render(request, 'registrations/message.html', context)

            context = {
                'error_heading': "Emails sent",
                'message': "Login credentials have been mailed to the corresponding new participants.",
                'url':request.build_absolute_uri(reverse('regsoft:firewallz_home'))
            }
            return render(request, 'registrations/message.html', context)
    else:
        colleges = College.objects.all()
        guests = Participant.objects.filter(is_guest=True)
        return render(request, 'regsoft/add_guest.html', {'colleges':colleges, 'guests':guests})

@staff_member_required
def add_participant(request):
    if request.method == 'POST':
        data = request.POST
        email = data['email']
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            messages.warning(request,'Please enter a valid email address.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            try:
                Participant.objects.get(email=data['email'])
                messages.warning(request,'Email already registered.')
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                pass
            try:
                events = data.getlist('events')
            except:
                messages.warning(request,'Please select event(s).')
                return redirect(request.META.get('HTTP_REFERER'))
            participant = Participant()
            participant.name = str(data['name'])
            participant.gender = str(data['gender'])
            participant.city = str(data['city'])
            participant.email = str(data['email'])
            participant.college = College.objects.get(name=str(data['college']))
            participant.phone = int(data['phone'])
            participant.email_verified = True
            participant.pcr_final = True
            participant.pcr_approved = True
            participant.save()
            ems_code = str(participant.college.id).rjust(3,'0') + str(participant.id).rjust(4,'0')
            participant.ems_code = ems_code
            encoded = gen_barcode(participant)
            participant.save()
            username = participant.name.split(' ')[0] + str(participant.id)
            password = ''.join(choice(chars) for _ in xrange(8))
            user = User.objects.create_user(username=username, password=password)
            participant.user = user
            participant.save()
            college = participant.college
            if not college.participant_set.filter(is_cr=True):
                participant.is_cr = True
                participant.save()
            for key in data.getlist('events'):
                event = Event.objects.get(id=int(key))
                Participation.objects.create(event=event, participant=participant, pcr_approved=True)
            participant.save()

            send_to = participant.email
            name = participant.name
            body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
			<center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
			<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 47th edition of OASIS, the annual cultural fest of Birla Institute of Technology & Science, Pilani, India. This year, OASIS will be held from October 31st to November 4th.             
           
This is to inform you that your guest registration is complete.
You can now login in the app using the following credentials and get your exclusive qrcode:
username : '%s'
password : '%s'

Regards,
StuCCAn (Head)
Dept. of Publications & Correspondence, OASIS 2017
BITS Pilani
%s
pcr@bits-oasis.org
</pre>
			''' %(name, username, password, get_pcr_number())
            sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
            from_email = Email('register@bits-oasis.org')
            to_email = Email(send_to)
            subject = "Registration for OASIS '17 REALMS OF FICTION"
            content = Content('text/html', body)

            try:
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
            except :
                participant.user = None
                participant.save()
                user.delete()
                participant.delete()
                context = {
                    'url':request.build_absolute_uri(reverse('regsoft:firewallz_home')),
                    'error_heading': "Error sending mail",
                    'message': "Sorry! Error in sending email. Please try again.",
                }
                return render(request, 'registrations/message.html', context)

            context = {
                'error_heading': "Emails sent",
                'message': "Login credentials have been mailed to the corresponding new participants.",
                'url':request.build_absolute_uri(reverse('regsoft:firewallz_home'))
            }
            return render(request, 'registrations/message.html', context)
    else:
        event_list = Event.objects.all()
        colleges = College.objects.all()
        guests = Participant.objects.filter(is_guest=True)
        return render(request, 'regsoft/add_participant.html', {'event_list':event_list,'colleges':colleges, 'guests':guests})


@staff_member_required
def show_uploads(request, p_id):
    part = get_object_or_404(Participant, id=p_id)
    try:
		profile_url = part.profile_pic.url
		docs_url = part.verify_docs.url
    except:
        message = part.name + '\'s Profile not complete yet.'
        messages.warning(request, message)
        return redirect(request.META.get('HTTP_REFERER'))
    return render(request, 'regsoft/show_uploads.html', {'participant':part})

@staff_member_required
def remove_guests(request):
    if request.method == 'POST':
        data = request.POST
        try:
            list = data.getlist('guest_list')
        except:
            messages.warning(request, 'No guest selected.')
            return redirect(request.META.get('HTTP_REFERER'))
        Participant.objects.filter(id__in=data.getlist('guest_list'), is_guest=True).delete()
        return redirect(reverse('regsoft:add_guest'))

@staff_member_required
def get_group_list(request, g_id):
    group = get_object_or_404(Group, id=g_id)
    if request.method == 'POST':
        try:
            data = request.POST
            id_list = data.getlist('id_list')
        except:
            return redirect(request.META.get('HTTP_REFERER'))

        participant_list = Participant.objects.filter(id__in=id_list)
        for participant in participant_list:
            if participant.is_g_leader:
                messages.warning(request,'Cannot unconfirm a Group Leader.')
                continue
            participant.group = None
            participant.firewallz_passed = False
            participant.save()
        leader = get_group_leader(group)
        if group.participant_set.count == 0:
            group.delete()
        return redirect(reverse('regsoft:firewallz_approval', kwargs={'c_id':leader.college.id}))
    participant_list = group.participant_set.all()
    return render(request, 'regsoft/group_list.html', {'participant_list':participant_list, 'group':group})

@staff_member_required
def delete_group(request, g_id):
    group = get_object_or_404(Group, id=g_id)
    leader = get_group_leader(group)
    for part in group.participant_set.all():
        part.firewallz_passed = False
        part.is_g_leader = False
        part.save()
    group.delete()
    return redirect(reverse('regsoft:firewallz_approval', kwargs={'c_id':leader.college.id}))

########################################## End Firewallz #########################################################################

############################################# RecNAcc for the One ################################################################

@staff_member_required
def recnacc_home(request):
    rows = [{'data':[group.group_code, get_group_leader(group).name, get_group_leader(group).college.name, get_group_leader(group).phone,group.created_time, group.participant_set.filter(controlz=True).count(), group.participant_set.filter(controlz=True, acco=True, checkout_group=None).count(), group.participant_set.filter(checkout_group__isnull=False).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:allocate_participants', kwargs={'g_id':group.id})), 'title':'Allocate Participants'}]} for group in Group.objects.all().order_by('-created_time')]
    headings = ['Group Code', 'Group Leader', 'College', 'Gleader phone', 'Firewallz passed time', 'Total controls passed','Total alloted', 'Checkout','View Participants']
    title = 'Groups that have passed firewallz'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def allocate_participants(request, g_id):
    group = get_object_or_404(Group, id=g_id)
    if request.method == 'POST':
        from datetime import datetime
        data = request.POST
        try:
            group.amount_deduct = data['amount_retained']
            group.save()
        except:
            pass
        if data['action'] == 'allocate':
            try:
                parts_id = data.getlist('data')
                room_id = data['room']
                room = Room.objects.get(id=room_id)
            except:
                messages.warning(request,'Incomplete selection')
                return redirect(request.META.get('HTTP_REFERER'))
            if not parts_id:
                messages.warning(request,'Incomplete selection')
                return redirect(request.META.get('HTTP_REFERER')) 
            rows = []
            room.vacancy -= len(parts_id)
            room.save()
            for part_id in parts_id:
                part = Participant.objects.get(id=part_id)
                part.acco = True
                part.room = room
                part.recnacc_time = datetime.now()
                part.save()
        elif data['action'] == 'deallocate':
            try:
                parts_id = data.getlist('data')
            except:
                return redirect(request.META.get('HTTP_REFERER'))
            for part_id in parts_id:
                part = Participant.objects.get(id=part_id)
                room = part.room
                room.vacancy += 1
                room.save()
                part.acco = False
                part.room = None
                part.save()
        return redirect(reverse('regsoft:recnacc_group_list', kwargs={'c_id':get_group_leader(group).college.id}))
    else:
        unalloted_participants = group.participant_set.filter(acco=False, checkout_group=None, controlz=True)
        alloted_participants = group.participant_set.filter(acco=True, checkout_group=None, controlz=True)
        checked_out = group.participant_set.filter(checkout_group__isnull=False)
        rooms_list = Room.objects.all()
        return render(request, 'regsoft/allot.html', {'unalloted':unalloted_participants, 'alloted':alloted_participants, 'rooms':rooms_list, 'group':group, 'checked_out':checked_out})

@staff_member_required
def recnacc_group_list(request, c_id):
    college = get_object_or_404(College, id=c_id)
    group_list = [group for group in Group.objects.all() if get_group_leader(group).college == college]
    complete_groups = [group for group in group_list if all(part.acco for part in group.participant_set.filter(controlz=True))]
    complete_rows = [{'data':[group.created_time, get_group_leader(group).name, group.participant_set.filter(controlz=True).count(), group.participant_set.filter(acco=True,checkout_group=None, controlz=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:allocate_participants', kwargs={'g_id':group.id})), 'title':'Manage group'}]} for group in complete_groups]
    incomplete_groups = [group for group in group_list if not group in complete_groups]
    incomplete_rows = [{'data':[group.created_time, get_group_leader(group).name, group.participant_set.filter(controlz=True).count(), group.participant_set.filter(acco=True,checkout_group=None, controlz=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:allocate_participants', kwargs={'g_id':group.id})), 'title':'Manage group'}]} for group in incomplete_groups]
    incomplete_table = {
        'rows':incomplete_rows,
        'headings':['Creaetd Time', 'GroupLeader Name', 'Total', 'Alloted', 'Manage'],
        'title':'Incompletely Alloted Groups from ' + college.name 
    }
    complete_table = {
        'rows':complete_rows,
        'headings':['Creaetd Time', 'GroupLeader Name', 'Total', 'Alloted', 'Manage'],
        'title':'Completely Alloted Groups from ' + college.name 
    }
    return render(request, 'regsoft/tables.html', {'tables':[incomplete_table, complete_table], 'college':college})

@staff_member_required
def room_details(request):
    room_list = Room.objects.all()
    rows = [{'data':[room.room, room.bhavan.name, room.vacancy, room.capacity,], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:manage_vacancies', kwargs={'r_id':room.id})), 'title':'Manage'},]} for room in room_list]
    headings = ['Room', 'Bhavan', 'Vacancy', 'Capacity', 'Manage Room Details']
    title = 'Manage Room Details'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def manage_vacancies(request, r_id):
    room = get_object_or_404(Room, id=r_id)
    if request.method == 'POST':
        data = request.POST
        try:
            note = data['note']
        except:
            messages.warning(request, 'Please add a note.')
        try:
            room.vacancy = data['vacancy']
            room.save()
        except:
            pass
        try:
            capacity = room.capacity
            vacancy = int(data['capacity']) - capacity
            room.vacancy = int(room.vacancy) + vacancy
            room.capacity = data['capacity']
            room.save()
        except:
            pass
        re_note = Note()
        re_note.note = note
        re_note.room = room
        re_note.save()
        return redirect(reverse('regsoft:room_details'))
    else:
        notes = room.note_set.all()
        return render(request, 'regsoft/manage_vacancies.html', {'room':room, 'notes':notes})

@staff_member_required
def recnacc_bhavans(request):
    rows =[{'data':[bhavan.name, reduce(lambda x,y:x+y.vacancy, bhavan.room_set.all(), 0),], 'link':[{'title':'Details', 'url':request.build_absolute_uri(reverse('regsoft:bhavan_details', kwargs={'b_id':bhavan.id}))},] } for bhavan in Bhavan.objects.all()]
    headings = ['Bhavan', 'Vacancy', 'Room-wise details']
    tables = [{'title':'All Bhavans', 'headings':headings, 'rows':rows}]
    return render(request,'regsoft/tables.html', {'tables':tables})

@staff_member_required
def bhavan_details(request, b_id):
	bhavan = Bhavan.objects.get(id=b_id)
	rows = [{'data':[room.room, room.vacancy, room.capacity], 'link':[{'title':'Details', 'url':request.build_absolute_uri(reverse('regsoft:manage_vacancies', kwargs={'r_id':room.id}))},]} for room in bhavan.room_set.all()]
	headings = ['Room', 'Vacancy', 'Capacity', 'Manage Vacancies']
	tables = [{'title': 'Details for ' + bhavan.name + ' bhavan', 'headings':headings, 'rows':rows}]
	return render(request, 'regsoft/tables.html', {'tables':tables})

@staff_member_required
def group_vs_bhavan(request):
    rows = []
    for group in Group.objects.all():
        if group.participant_set.filter(acco=True):
            bhavans = []
            for part in group.participant_set.filter(acco=True):
                if not part.room.bhavan in bhavans:
                    bhavans.append(part.room.bhavan)
            for bhavan in bhavans:
                rows.append({'data':[bhavan.name,get_group_leader(group).college.name,group.group_code, get_group_leader(group).name, group.participant_set.filter(acco=True, room__bhavan=bhavan).count(), get_group_leader(group).phone],'link':[]})
    table = {
        'rows':rows,
        'headings':['Bhavan','College','Group Code', 'Group Leader', 'Number of participants in bhavan', 'Group Leader Phone'],
        'title':'Group vs Bhavans'
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def recnacc_college_details(request):
    college_list = []
    for c in College.objects.all():
        try:
            p = c.participant_set.get(is_cr=True)
            college_list.append(c)
        except:
            pass
    rows = [{'data':[college.name, college.participant_set.get(is_cr=True).name,college.participant_set.filter(acco=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:recnacc_group_list', kwargs={'c_id':college.id})), 'title':'View Details'}]} for college in college_list]
    headings = ['College', 'Cr Name','Alloted Participants', 'View Details']
    title = 'Select college to approve Participants'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def college_detail(request, c_id):
    rows = []
    college = get_object_or_404(College, id=c_id)
    for group in Group.objects.all():
        if get_group_leader(group).college == college:
            if group.participant_set.filter(acco=True):
                bhavans = []
                for part in group.participant_set.filter(acco=True):
                    if not part.room.bhavan in bhavans:
                        bhavans.append(part.room.bhavan)
                for bhavan in bhavans:
                    rows.append({'data':[bhavan.name,get_group_leader(group).college.name,group.group_code, get_group_leader(group).name, group.participant_set.filter(acco=True, room__bhavan=bhavan).count(), get_group_leader(group).phone],'link':[]})
    table = {
        'rows':rows,
        'headings':['Bhavan','College','Group Code', 'Group Leader', 'Number of participants in bhavan', 'Group Leader Phone'],
        'title':'Group vs Bhavans from ' + college.name,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def checkout_college(request):
	rows = [{'data':[college.name,college.participant_set.filter(acco=True).count(), college.participant_set.filter(checkout_group__isnull=False).count()],'link':[{'title':'Checkout', 'url':request.build_absolute_uri(reverse('regsoft:checkout', kwargs={'c_id':college.id}))}] } for college in College.objects.all()]
	tables = [{'title':'List of Colleges', 'rows':rows, 'headings':['College', 'Alloted Participants', 'Checked out Participants','Checkout']}]
	return render(request, 'regsoft/tables.html', {'tables':tables})

@staff_member_required
def master_checkout(request):
    ck_group_list = CheckoutGroup.objects.all()
    rows = [{'data':[ck_group.participant_set.all()[0].college.name,ck_group.participant_set.all().count(), ck_group.created_time, ck_group.amount_retained], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:ck_group_details', kwargs={'ck_id':ck_group.id})), 'title':'View Details'}]} for ck_group in ck_group_list]
    headings = ['College', 'Participant Count', 'Time of Checkout', 'Amount Retained', 'View Details']
    title = 'All Checkout groups'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    amount = 0
    for ck_group in CheckoutGroup.objects.all():
        amount += ck_group.amount_retained
    return render(request, 'regsoft/master_checkout.html', {'tables':[table,], 'amount':amount})

@staff_member_required
def checkout(request, c_id):
    college = get_object_or_404(College, id=c_id)
    if request.method == 'POST':
        data = request.POST
        try:
            part_list = Participant.objects.filter(id__in=data.getlist('part_list'))
        except:
            return redirect(request.META.get('HTTP_REFERER'))

        checkout_group = CheckoutGroup.objects.create()
        print data['retained']
        # try:
        checkout_group.amount_retained = int(data['retained'])
        checkout_group.save()
        # except:
        #     pass
        for participant in part_list:
            room = participant.room
            room.vacancy += 1
            room.save()
            participant.checkout_group = checkout_group
            participant.acco = False
            participant.save()
        encoded = generate_ckgroup_code(checkout_group)
        checkout_group.save()
        return redirect(reverse('regsoft:checkout_groups', kwargs={'c_id':college.id}))
    participant_list = college.participant_set.filter(acco=True)
    return render(request, 'regsoft/checkout.html', {'college':college, 'part_list':participant_list})

@staff_member_required
def checkout_groups(request, c_id):
    college = get_object_or_404(College, id=c_id)
    ck_group_list = [ck_group for ck_group in CheckoutGroup.objects.all() if ck_group.participant_set.all()[0].college == college]
    rows = [{'data':[ck_group.participant_set.all().count(), ck_group.created_time, ck_group.amount_retained], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:ck_group_details', kwargs={'ck_id':ck_group.id})), 'title':'View Details'}]} for ck_group in ck_group_list]
    headings = ['Participant Count', 'Time of Checkout', 'Amount Retained', 'View Details']
    title = 'Checkout groups from ' + college.name
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def ck_group_details(request, ck_id):
    checkout_group = get_object_or_404(CheckoutGroup, id=ck_id)
    rows = [{'data':[part.name, part.phone, part.email, part.gender, get_event_string(part), part.room.room, part.room.bhavan.name], 'link':[]} for part in checkout_group.participant_set.all()]
    headings = ['Name', 'Phone', 'Email', 'Gender', 'Events', 'Room', 'Bhavan']
    title = 'Checkout detail at ' + str(checkout_group.created_time) + ', Amount Retained:' + str(checkout_group.amount_retained)
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,],})

############################################ Hope she likes it ;) ############################### PS Shitty comments coz gitlab! Hopefully yaad rhega change krna hai. Else divyam, sanchit, hemant, dekh lena

########################################### Controlz and not recnacc coz avvvaaaaaaaaannnnnnttttttiiiiiii lite####################
@staff_member_required
def controls_home(request):
    rows = [{'data':[group.group_code, get_group_leader(group).name, get_group_leader(group).college.name, get_group_leader(group).phone,group.created_time, group.participant_set.filter(is_guest=False).count(), group.participant_set.filter(controlz=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:create_bill', kwargs={'g_id':group.id})), 'title':'Create Bill'}]} for group in Group.objects.all()]
    headings = ['Group Code', 'Group Leader', 'College', 'Gleader phone', 'Firewallz passed time', 'Total in group', 'Passed controls from group','View Participants']
    title = 'Groups that have passed firewallz'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def create_bill(request, g_id):
    group  = get_object_or_404(Group, id=g_id)
    controlz_passed = group.participant_set.filter(controlz=True, is_guest=False)
    controlz_unpassed = group.participant_set.filter(controlz=False, is_guest=False)
    if request.method == 'POST':
        data = request.POST
        try:
            id_list = data.getlist('data')
        except:
            messages.warning(request, 'Please select participants')
            return redirect(request.META.get('HTTP_REFERER'))
        if not id_list:
            messages.warning(request, 'Please select participants')
            return redirect(request.META.get('HTTP_REFERER'))
        bill = Bill()
        bill.two_thousands = data['twothousands']
        bill.five_hundreds = data['fivehundreds']
        bill.two_hundreds = data['twohundreds']
        bill.hundreds = data['hundreds']
        bill.fifties = data['fifties']
        bill.twenties = data['twenties']
        bill.tens = data['tens']
        bill.two_thousands_returned = data['twothousandsreturned']
        bill.five_hundreds_returned = data['fivehundredsreturned']
        bill.two_hundreds_returned = data['twohundredsreturned']
        bill.hundreds_returned = data['hundredsreturned']
        bill.fifties_returned = data['fiftiesreturned']
        bill.twenties_returned = data['twentiesreturned']
        bill.tens_returned = data['tensreturned']
        amount_dict = {'twothousands':2000, 'fivehundreds':500, 'twohundreds':200,'hundreds':100, 'fifties':50, 'twenties':20, 'tens':10}
        return_dict = {'twothousandsreturned':2000, 'fivehundredsreturned':500, 'twohundredsreturned':200,'hundredsreturned':100, 'fiftiesreturned':50, 'twentiesreturned':20, 'tensreturned':10}
        bill.amount = 0
        for key,value in amount_dict.iteritems():
            bill.amount += int(data[key])*int(value)
        for key,value in return_dict.iteritems():
            bill.amount -= int(data[key])*int(value)

        try:
            bill.draft_number = data['draft_number']
        except:
            pass
        bill.draft_amount = data['draft_amount']
        bill.amount += int(bill.draft_amount)
        if not (bill.amount == 0 and bill.draft_amount == 0):
            bill.save()
            for p_id in id_list:
                part = Participant.objects.get(id=p_id)
                part.bill = bill
                part.controlz = True
                part.curr_controlz_paid = True
                part.curr_paid = True
                part.save()
            return redirect(reverse('regsoft:bill_details', kwargs={'b_id':bill.id}))
        else:
            messages.warning(request, 'Please enter a bill amount.')
            return redirect(reverse('regsoft:create_bill', kwargs={'g_id':group.id}))
    else:
        return render(request, 'regsoft/controls_group.html', {'controlz_passed':controlz_passed, 'controlz_unpassed':controlz_unpassed, 'group':group})

@staff_member_required
def show_all_bills(request):
    rows = [{'data':[college.name, college.participant_set.filter(controlz=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:show_college_bills', kwargs={'c_id':college.id})), 'title':'Show bills'}]} for college in College.objects.all()]
    headings = ['College', 'Controls passed participants', 'Show bills',]
    title = 'Colleges for bill details'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def show_college_bills(request, c_id):
    college = College.objects.get(id=c_id)
    bills = []
    for part in college.participant_set.filter(controlz=True):
        if part.bill not in bills:
            bills.append(part.bill)
    rows = [{'data':[bill.time_paid, bill.participant_set.filter(gender='M').count(), bill.participant_set.filter(gender='F').count(), bill.amount], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:bill_details', kwargs={'b_id':bill.id})), 'title':'View Details'}]} for bill in bills]
    headings = ['Time Created', 'Male Participants', 'Female Participants', 'Amount', 'Details']
    title = 'Bills created for ' + college.name
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def bill_details(request, b_id):
    from datetime import datetime
    time_stamp = datetime.now()
    bill = get_object_or_404(Bill, id=b_id)
    participants = bill.participant_set.all()
    college = participants[0].college
    bill = get_object_or_404(Bill, id=b_id)
    c_rows = [{'data':[part.name, get_event_string(part), bill.time_paid, get_amount(part)], 'link':[]} for part in bill.participant_set.all()]
    table = {
		'title' : 'Participant details for the bill from ' + college.name +'. Cash amount = Rs ' + str(bill.amount-bill.draft_amount) + '. Draft Amount = Rs ' + str(bill.draft_amount),
		'headings' : ['Name', 'Event(s)', 'Time created','Had to pay'],
		'rows':c_rows,
	}
    return render(request, 'regsoft/bill_details.html', {'tables':[table,],'bill':bill, 'participant_list':participants, 'college':college, 'curr_time':time_stamp})

def get_amount(part):
    if part.controlz_paid and part.paid:
        return 0
    elif part.paid:
        return 700
    else:
        return 1000

@staff_member_required
def print_bill(request, b_id):
    from datetime import datetime
    time = datetime.now()
    bill = get_object_or_404(Bill, id=b_id)
    participants = bill.participant_set.all()
    if not participants:
        return redirect(reverse('regsoft:bill_details', kwargs={'b_id':bill.id}))
    college = participants[0].college
    g_leader = bill.participant_set.all()[0].group.participant_set.get(is_g_leader=True)
    draft = bill.draft_number
    if not draft:
        draft = 'null'
    payment_methods = [{'method':'Cash', 'amount':bill.amount-bill.draft_amount}, {'method':'Draft #'+draft, 'amount':bill.draft_amount}]
    return render(request, 'regsoft/bill_invoice.html', {'bill':bill, 'part_list':participants, 'college':college, 'payment_methods':payment_methods, 'time':time, 'cr':g_leader})

@staff_member_required
def delete_bill(request, b_id):
    bill = get_object_or_404(Bill, id=b_id)
    participants = bill.participant_set.all()
    for part in participants:
        part.controlz = False
        part.curr_controlz_paid = False
        part.curr_paid = False
        part.save()
    college = participants[0].college
    bill.delete()
    return redirect(reverse('regsoft:show_college_bills', kwargs={'c_id':college.id}))

@staff_member_required
def recnacc_list(request):
    rows = [{'data':[group.group_code, get_group_leader(group).name, get_group_leader(group).college.name, get_group_leader(group).phone,group.created_time, group.participant_set.filter(controlz=True).count(), group.participant_set.filter(controlz=True, acco=True, checkout_group=None).count(), group.participant_set.filter(checkout_group__isnull=False).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:recnacc_list_group', kwargs={'g_id':group.id})), 'title':'Select Participants'}]} for group in Group.objects.all().order_by('-created_time')]
    headings = ['Group Code', 'Group Leader', 'College', 'Gleader phone', 'Firewallz passed time', 'Total controls passed','Total alloted', 'Checkout','View Participants']
    title = 'Groups that have been alloted'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def recnacc_list_group(request, g_id):
    group = get_object_or_404(Group, id=g_id)
    participant_list = group.participant_set.filter(acco=True).order_by('-recnacc_time')
    return render(request, 'regsoft/recnacc_list.html', {'participant_list':participant_list, 'college':get_group_leader(group).college})

@staff_member_required
def generate_recnacc_list(request):
    if request.method == 'POST':
        data = request.POST
        id_list = data.getlist('data')
        c_rows = []
        for p_id in id_list:
            part = Participant.objects.get(id=p_id)
            c_rows.append({'data':[part.name, part.college.name, part.gender,get_cr_name(part), get_event_string(part), part.room.room, part.room.bhavan, 400], 'link':[]})
        part = Participant.objects.get(id=id_list[0])
        amount = (len(id_list))*400
        c_rows.append({'data':['Total', '','','','','','',amount]})
        table = {
            'title':'Participant list for RecNAcc from ' + part.college.name,
            'headings':['Name', 'College', 'Gender', 'CR Name', 'Event(s)', 'Room','Bhavan', 'Caution Deposit'],
            'rows': c_rows
        }
        return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def get_profile_card(request):
    rows = [{'data':[part.name, part.phone, part.email, part.gender, get_event_string(part)], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:get_profile_card_participant', kwargs={'p_id':part.id})), 'title':'Get profile card'}]} for part in Participant.objects.filter(Q(pcr_final=True) | Q(is_guest=True))]
    headings = ['Name', 'Phone', 'Email', 'Gender', 'Events', 'Get profile card']
    title = 'Generate Profile Card'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,],})

@staff_member_required
def get_profile_card_group(request, g_id):
    group = get_object_or_404(Group, id=g_id)
    part_list = group.participant_set.all()
    url = request.build_absolute_uri(reverse('registrations:generate_qr'))
    return render(request, 'regsoft/card.html', {'part_list':part_list, 'url':url})

@staff_member_required
def contacts(request):
	return render(request, 'regsoft/contact.html')

@staff_member_required
def user_logout(request):
	logout(request)
	return redirect('regsoft:index')