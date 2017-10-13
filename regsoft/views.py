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

############################### Helper Function ########################################################

def get_group_leader(group):
    return Participant.objects.get(group=group, is_g_leader=True)

def get_event_string(participant):
    participation_set = Participation.objects.filter(participant=participant, pcr_approved=True)
    events = ''
    for participation in participation_set:
        events += participation.event.name + ', '
    events = events[:-2]
    return events

########################################### Controlz and not recnacc coz avvvaaaaaaaaannnnnnttttttiiiiiii lite####################3
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
        amount = (len(id_list))*300
        c_rows.append({'data':['Total', '','','','','','',amount]})
        table = {
            'title':'Participant list for RecNAcc from ' + part.college.name,
            'headings':['Name', 'College', 'Gender', 'CR Name', 'Events', 'Room','Bhavan', 'Caution Deposit'],
            'rows': c_rows
        }
        return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def get_profile_card(request, p_id):
    participant = get_object_or_404(Participant, id=p_id)
    events = get_event_string(participant)
    return render(request, 'registrations/profile_card.html', {'participant':participant, 'events':events,})