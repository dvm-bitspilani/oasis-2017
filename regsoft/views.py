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
from pcradmin.views import get_cr_name
from django.contrib import messages

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
	group.group_code = 'oasis_group' + college_code + group_ida
	group.save()
	return encoded

########################################### End Of Helper Functions ##############################################################
@staff_member_required
def index(request):
	if request.user.username.lower() == 'controlz':
		return redirect(reverse('regsoft:controlz_home'))
	if request.user.username.lower() == 'recnacc':
		return redirect(reverse('regsoft:recnacc_home'))
	if request.user.username == 'firewallz' or request.user.is_superuser:
		return redirect(reverse('regsoft:firewallz_home'))

########################################### Firewallz coz they're pretty sweet people ############################################

@staff_member_required
def firewallz_home(request):
    college_list = College.objects.all()
    rows = [{'data':[college.name, college.participant_set.get(college=college, is_cr=True).name,college.participant_set.filter(pcr_final=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:firewallz_approval', kwargs={'c_id':college.id})), 'title':'Approve Participants'}]} for college in college_list]
    headings = ['College', 'CR', 'PCr Finalised Participants', 'Approve Participants']
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
            part.firewallz_passed=True
            part.group = group
            part.save() 
        encoded = generate_group_code(group)
        group.save()
        return redirect('regsoft:firewallz_home')
    
    groups_passed = [group for group in Group.objects.all() if get_group_leader(group).college == college]
    unapproved_list = college.participant_set.filter(pcr_final=True, firewallz_passed=False)
    print groups_passed
    return render(request, 'regsoft/firewallz_approval.html', {'groups_passed':groups_passed, 'unapproved_list':unapproved_list, 'college':college})

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
            participant.group = None
            participant.firewallz_passed = False
            participant.save()
        if group.participant_set.count == 0:
            group.delete()
        return redirect(reverse('regsoft:firewallz_approval', kwargs={'c_id':get_group_leader(group).college.id}))
    participant_list = group.participant_set.all()
    return render(request, 'regsoft/group_list.html', {'participant_list':participant_list, 'group':group})

########################################## End Firewallz #########################################################################

############################################# RecNAcc for the One ################################################################

@staff_member_required
def recnacc_home(request):
    rows = [{'data':[group.group_code, get_group_leader(group).name, get_group_leader(group).college.name, get_group_leader(group).phone,group.created_time], 'link':[{'url':request.build_absolute_uri('regsoft:allocate_participants', kwargs={'g_id':group.id}), 'title':'Allocate Participants'}]} for group in Group.objects.all().order_by('-created_time')]
    headings = ['Group Code', 'Group Leader', 'College', 'Gleader phone', 'Firewallz passed time', 'View Participants']
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
                room_id = data['room']
                room = Room.objects.get(id=room_id)
            except:
                return redirect(request.META.get('HTTP_REFERER'))
                
            rows = []
            room.vacancy += len(parts_id)
            room.save()
            for part_id in parts_id:
                part = Participant.objects.get(id=part_id)
                part.acco = False
                part.room = None
                part.save()
        return redirect(reverse('regsoft:recnacc_group_list', kwargs={'c_id':get_group_leader(group).college.id}))
    else:
        unalloted_participants = group.participant_set.filter(acco=False)
        alloted_participants = group.participant_set.filter(acco=True)
        rooms_list = Room.objects.all()
        return render(request, 'regsoft/allot.html', {'unalloted':unalloted_participants, 'alloted':alloted_participants, 'rooms':rooms_list})

@staff_member_required
def recnacc_group_list(request, c_id):
    college = get_object_or_404(College, id=c_id)
    group_list = [group for group in Group.objects.all() if get_group_leader(group).college == college]
    complete_groups = [group for group in group_list if all(part.acco for part in group.participant_set.all())]
    incomplete_groups = [group for group in group_list if not group in complete_groups]

    return render(request, 'regsoft/recnacc_group_list.html', {'complete_groups':complete_groups, 'incomplete_groups':incomplete_groups})

@staff_member_required
def room_details(request):
    room_list = Room.objects.all()
    rows = [{'data':[room.name, room.bhavan.name, room.vacancy, room.capacity,], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:manage_vacancies', kwargs={'r_id':room.id})), 'title':'Manage'},]} for room in room_list]
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
            room.vacancy = data['vacancy']
            room.save()
        except:
            pass
        try:
            room.capacity = data['capacity']
            room.save()
        except:
            pass
        return redirect(reverse('regsoft:room_details'))
    else:
        return render(request, 'regsoft/manage_vacanacies.html', {'room':room})

@staff_member_required
def recnacc_bhavans(request):
    rows =[{'data':[bhavan.name, reduce(lambda x,y:x+y.vacancy, bhavan.room_set.all(), 0),], 'link':[{'title':'Details', 'url':reverse('regsoft:bhavan_details', kwargs={'b_id':bhavan.id})},] } for bhavan in Bhavan.objects.all()]
    headings = ['Bhavan', 'Vacancy', 'Room-wise details']
    tables = [{'title':'All Bhavans', 'headings':headings, 'rows':rows}]
    return render(request,'regsoft/tables.html', {'tables':tables})

@staff_member_required
def bhavan_details(request, b_id):
	bhavan = Bhavan.objects.get(id=b_id)
	rows = [{'data':[room.room, room.vacancy, room.capacity], 'link':[]} for room in bhavan.room_set.all()]
	headings = ['Room', 'Vacancy', 'Capacity']
	tables = [{'title': 'Details for ' + bhavan.name + ' bhavan', 'headings':headings, 'rows':rows}]
	return render(request, 'regsoft/tables.html', {'tables':tables})

@staff_member_required
def recnacc_college_details(request):
    college_list = College.objects.all()
    rows = [{'data':[college.name, Participant.objects.get(college=college, is_cr=True).name,college.participant_set.filter(pcr_final=True).count()], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:college_detail', kwargs={'c_id':college.id})), 'title':'View Details'}]} for college in college_list]
    headings = ['College', 'Alloted Participants', 'View Details']
    title = 'Select college to approve Participants'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def college_detail(request, c_id):
    college = get_object_or_404(College, id=c_id)
    rows = [{'data':[get_group_leader(group).name, get_group_leader(group).phone, get_group_leader(group).email,group.participant_set.filter(acco=True).count(), get_group_leader(group).room.room, get_group_leader(group).room.bhavan.name], 'link':[]} for group in Group.objects.all() if get_group_leader(group).college == college]
    headings = ['Group Leader', 'GLeader Phone', 'GLeader Email','Participants Count', 'Room', 'Bhavan']
    title = 'Groups alloted from ' + college.name
    table = {
        'rows':rows,
        'headings':headings,
        'title':title
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def checkout_college(request):
	rows = [{'data':[college.name,college.participant_set.filter(acco=True).count(),],'link':[{'title':'Checkout', 'url':reverse('regsoft:checkout', kwargs={'c_id':college.id})}] } for college in College.objects.all()]
	tables = [{'title':'List of Colleges', 'rows':rows, 'headings':['College', 'Alloted Participants', 'Checkout']}]
	return render(request, 'regsoft/tables.html', {'tables':tables})

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

        try:
            checkout_group.amount_retained = data['amount_retained']
        except:
            pass
        for participant in part_list:
            room = participant.room
            room.vacany += 1
            room.save()
            participant.room = None
            participant.checkout_group = checkout_group
            participant.acco = False
            participant.checkout = True
            participant.save()
        return redirect(reverse('regsoft:checkout_groups', kwargs={'c_id':college.id}))
    participant_list = college.participant_set.filter(acco=True)
    return render(request, 'regsoft/checkout.html', {'college':college, 'participant_list':participant_list})

@staff_member_required
def checkout_groups(request, c_id):
    college = get_object_or_404(College, id=c_id)
    ck_group_list = [ck_group for ck_group in CheckoutGroup.objects.all() if ck_group.participant_set.all()[0].college == college]
    ck_group_list = ck_group_list.order_by('-created_time')
    rows = [{'data':[ck_group.participant_set.all().count(), ck_group.created_time, ck_group.amount_retained], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:ck_group_details', kwargs={'ck_id':ck_group.id})), 'title':'View Details'}]} for ck_group in ck_group_list]
    headings = ['Participant Count', 'Time of Checkout', 'Amount Retained', 'View Details']
    title = 'Checkout groups from ' + colllege.name
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def ck_group_details(request, ck_id):
    checkout_group = get_object_or_404(CheckoutGroup, id=ck_id)
    rows = [{'data':[part.name, part.phone, part.email, part.gender, get_event_string(part)],} for part in checkout_group.participant_set.all()]
    headings = ['Name', 'Phone', 'Email', 'Gender', 'Events']
    title = 'Checkout detail at ' + checkout_group.created_time + ', Amount Retained:' + checkout_group.amount_retained
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/checkout_details.html', {'tables':[table,], 'ck_group':checkout_group})

############################################ Hope she likes it ;) ############################### PS Shitty comments coz gitlab! Hopefully yaad rhega change krna hai. Else divyam, sanchit, hemant, dekh lena

########################################### Controlz and not recnacc coz avvvaaaaaaaaannnnnnttttttiiiiiii lite####################
@staff_member_required
def controlz_home(request):
    rows = [{'data':[group.group_code, get_group_leader(group).name, get_group_leader(group).college.name, get_group_leader(group).phone,group.created_time], 'link':[{'url':request.build_absolute_uri('regsoft:create_bill', kwargs={'g_id':group.id}), 'title':'Create Bill'}]} for group in Group.objects.all()]
    headings = ['Group Code', 'Group Leader', 'College', 'Gleader phone', 'Firewallz passed time', 'View Participants']
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
    paid_participants = group.participant_set.filter(Q(controlz_paid=True) | Q(curr_controlz_paid=True))
    unpaid_participants = group.participant_set.filter(controlz_paid=False, curr_controlz_paid=False)
    if request.method == 'POST':
        data = request.POST
        id_list = data.getlist('data')
        bill = Bill()
        bill.two_thousands = data['twothousands']
        bill.five_hundreds = data['fivehundreds']
        bill.hundreds = data['hundreds']
        bill.fifties = data['fifties']
        bill.twenties = data['twenties']
        bill.tens = data['tens']
        bill.two_thousands_returned = data['twothousandsreturned']
        bill.five_hundreds_returned = data['fivehundredsreturned']
        bill.hundreds_returned = data['hundredsreturned']
        bill.fifties_returned = data['fiftiesreturned']
        bill.twenties_returned = data['twentiesreturned']
        bill.tens_returned = data['tensreturned']
        amount_dict = {'twothousands':2000, 'fivehundreds':500, 'hundreds':100, 'fifties':50, 'twenties':20, 'tens':10}
        return_dict = {'twothousandsreturned':2000, 'fivehundredsreturned':500, 'hundredsreturned':100, 'fiftiesreturned':50, 'twentiesreturned':20, 'tensreturned':10}
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
			return redirect(reverse('regsoft:create_bill', kwargs={'g_id':group.id}))
    
    else:
        college = paid_participants[0].college
        return render(request, 'regsoft/controlz_group.html', {'paid':paid_participants, 'unpaid':unpaid_participants})

# @staff_member_required
# def controlz_participant_edit(request, p_id):
#     participant = get_object_or_404(Participant, id=p_id)
#     if request.method == 'POST':
#         name = request.POST['name']

@staff_member_required
def controlz_participant_add(request, g_id):
    group = get_object_or_404(Group, id=g_id)
    if request.method == 'POST':
        data = request.POST
        g_leader = get_group_leader(group)
        participant = Participant()
        participant.name = str(data['name'])
        participant.gender = str(data['gender'])
        participant.email = str(data['email'])
        participant.phone = int(data['phone'])
        participant.college = g_leader.college
        participant.group = group
        participant.firewallz_passed = True
        participant.pcr_final = True
        participant.save()
        for key in data.getlist('events[]'):
            event = Event.objects.get(id=int(key))
            Participation.objects.create(event=event, participant=participant)
        participant.save()
        return redirect(reverse('regsoft:create_bill', kwargs = {'g_id':group.id}))
    else:
        return render(request, 'regsoft/add_participant.html', {'group':group})
        
@staff_member_required
def show_all_bills(request, c_id):
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
    return render(request, 'regsoft/bill_details.html', {'bill':bill, 'participant_list':participants, 'college':college, 'curr_time':time_stamp})

@staff_member_required
def print_bill(request, b_id):
    bill = get_object_or_404(Bill, id=b_id)
    participants = bill.participant_set.all()
    college = participants[0].college
    try:
        draft = bill.draft_number
    except:
        draft = ''
    payment_methods = [{'method':'Cash', 'amount':bill.amount-bill.draft_amount}, {'method':'Draft #'+draft, 'amount':bill.draft_amount}]
    number = Bill.objects.all().count()
    return render(request, 'regsoft/bill_invoice.html', {'bill':bill, 'participant_list':participants, 'college':college, 'number':number, 'payment_methods':payment_methods})

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
    return redirect(reverse('regsoft:show_all_bills', kwargs={'c_id':college.id}))

@staff_member_required
def recnacc_list(request, c_id):
    college = get_object_or_404(College, id=c_id)
    participant_list = Participant.objects.filter(college=college, acco=True)
    participant_list.sort(key=lambda x: x.recnacc_time, reverse=True)
    return render(request, 'regsoft/recnacc_list.html', {'participant_list':participant_list})

@staff_member_required
def generate_recnacc_list(request):
    if request.method == 'POST':
        data = request.POST
        id_list = data.getlist('data')
        c_rows = []
        for p_id in id_list:
            part = Participant.objects.get(id=p_id)
            c_rows.append({'data':[part.name, part.college.name, part.gender,get_cr_name(part), get_event_string(part), part.room.room, part.room.bhavan, 300], 'link':[]})
        part = Participant.objects.get(id=id_list[0])
        amount = (len(id_list))*400
        c_rows.append({'data':['Total', '','','','','','',amount]})
        table = {
            'title':'Participant list for RecNAcc from ' + part.college.name,
            'headings':['Name', 'College', 'Gender', 'CR Name', 'Events', 'Room','Bhavan', 'Caution Deposit'],
            'rows': c_rows
        }
        return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def get_profile_card(request):
    rows = [{'data':[part.name, part.phone, part.email, part.gender, get_event_string(part)], 'link':[{'url':request.build_absolute_uri(reverse('regsoft:get_profile_card_participant', kwargs={'p_id':part.id})), 'title':'Get profile card'}]} for part in Participant.objects.filter(pcr_final=True)]
    headings = ['Name', 'Phone', 'Email', 'Gender', 'Events']
    title = 'Generate Profile Card'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'regsoft/tables.html', {'tables':[table,],})

@staff_member_required
def get_profile_card_participant(request, p_id):
    participant = get_object_or_404(Participant, id=p_id)
    events = get_event_string(participant)
    return render(request, 'registrations/profile_card.html', {'participant':participant, 'events':events,})

@staff_member_required
def contacts(request):
	return render(request, 'regsoft/contact.html')

@staff_member_required
def user_logout(request):
	logout(request)
	return redirect('regsoft:index')