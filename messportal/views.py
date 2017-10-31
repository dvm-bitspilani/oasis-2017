from django.shortcuts import render, get_object_or_404, redirect
from registrations.models import *
from events.models import *
from .models import *
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
import re

@staff_member_required
def index(request):
    return render(request, 'messportal/index.html')

@staff_member_required
def add_mess_item(request):
    if request.method == 'POST':
        data = request.POST
        item = Item()
        item.name = data['name']
        item.price = int(data['price'])
        item.save()
    items = Item.objects.all()
    return render(request, 'messportal/add_mess_item.html', {'items':items})

@staff_member_required
def add_prof_show(request):
    if request.method == 'POST':
        data = request.POST
        prof_show = ProfShow()
        prof_show.name = data['name']
        prof_show.price = int(data['price'])
        prof_show.appcontent = data['app_content']
        prof_show.date = data['date']
        prof_show.venue = data['venue']
        prof_show.contact = data['contact']
        prof_show.save()
    prof_shows = ProfShow.objects.all()
    return render(request, 'messportal/add_prof_show.html', {'prof_shows':prof_shows})

@staff_member_required
def edit_item(request, i_id):
    item = get_object_or_404(Item, id=i_id)
    if request.method == 'POST':
        data = request.POST
        item.name = data['name']
        item.price = int(data['price'])
        item.save()
        items = Item.objects.all()
        return render(request, 'messportal/add_mess_item.html', {'items':items})        
    return render(request, 'messportal/edit_item.html', {'item':item})

@staff_member_required
def edit_profshow(request, ps_id):
    profshow = get_object_or_404(ProfShow, id=ps_id)
    if request.method == 'POST':
        data = request.POST
        profshow.name = data['name']
        profshow.price = int(data['price'])
        profshow.appcontent = data['app_content']
        profshow.date = data['date']
        profshow.venue = data['venue']
        profshow.contact = data['contact']
        profshow.save()
        prof_shows = ProfShow.objects.all()
        return render(request, 'messportal/add_prof_show.html', {'prof_shows':prof_shows})        
    return render(request, 'messportal/edit_profshow.html', {'profshow':profshow})

@staff_member_required
def create_mess_bill(request):
    if request.method == 'POST':
        data = request.POST
        mess_bill = MessBill()
        mess_bill.item = Item.objects.get(id=data['item_id'])
        barcode = 'oasis17' + data['barcode']
        mess_bill.buyer_id = barcode
        mess_bill.quantity = data['count']
        mess_bill.mess = data['mess']
        mess_bill.n2000 = int(data['n_2000'])
        mess_bill.intake = 0
        mess_bill.outtake = 0
        if int(data['n_2000'])>0:
            mess_bill.intake += int(data['n_2000'])*2000
        else:
            mess_bill.outtake -= int(data['n_2000'])*2000
        mess_bill.n500 = int(data['n_500'])
        if int(data['n_500'])>0:
            mess_bill.intake += int(data['n_500'])*500
        else:
            mess_bill.outtake -= int(data['n_500'])*500
        mess_bill.n200 = int(data['n_200'])
        if int(data['n_200'])>0:
            mess_bill.intake += int(data['n_200'])*200
        else:
            mess_bill.outtake -= int(data['n_200'])*200
        mess_bill.n100 = int(data['n_100'])
        if int(data['n_100'])>0:
            mess_bill.intake += int(data['n_100'])*100
        else:
            mess_bill.outtake -= int(data['n_100'])*100
        mess_bill.n50 = int(data['n_50'])
        if int(data['n_50'])>0:
            mess_bill.intake += int(data['n_50'])*50
        else:
            mess_bill.outtake -= int(data['n_50'])*50
        mess_bill.n20 = int(data['n_20'])
        if int(data['n_20'])>0:
            mess_bill.intake += int(data['n_20'])*20
        else:
            mess_bill.outtake -= int(data['n_20'])*20
        mess_bill.n10 = int(data['n_10'])
        if int(data['n_10'])>0:
            mess_bill.intake += int(data['n_10'])*10
        else:
            mess_bill.outtake -= int(data['n_10'])*10
        mess_bill.amount = mess_bill.intake - mess_bill.outtake
        mess_bill.created_by = data['created_by']
        try:
            participant = Participant.objects.get(barcode=barcode)
        except:
            context = {
                'error_heading':'No match found',
                'message':'Participant does not exist.',
                'url':request.build_absolute_uri(reverse('messportal:index'))
            }
            profshow_bill.delete()
            return render(request, 'registrations/message.html', context)
        mess_bill.save()
        return redirect(reverse('messportal:view_all_mess_bills'))
    items = Item.objects.all()
    return render(request, 'messportal/create_mess_bill.html',{'items':items})

@staff_member_required
def create_profshow_bill(request):
    if request.method == 'POST':
        data = request.POST
        profshow_bill = ProfShowBill()
        prof_show = ProfShow.objects.get(id=data['prof_show'])
        profshow_bill.prof_show = prof_show
        profshow_bill.buyer_id = 'oasis17' + data['barcode']
        profshow_bill.quantity = int(data['count'])
        profshow_bill.n2000 = int(data['n_2000'])
        profshow_bill.intake = 0
        profshow_bill.outtake = 0
        if int(data['n_2000'])>0:
            profshow_bill.intake += int(data['n_2000'])*2000
        else:
            profshow_bill.outtake -= int(data['n_2000'])*2000
        profshow_bill.n500 = int(data['n_500'])
        if int(data['n_500'])>0:
            profshow_bill.intake += int(data['n_500'])*500
        else:
            profshow_bill.outtake -= int(data['n_500'])*500
        profshow_bill.n200 = int(data['n_200'])
        if int(data['n_200'])>0:
            profshow_bill.intake += int(data['n_200'])*200
        else:
            profshow_bill.outtake -= int(data['n_200'])*200
        profshow_bill.n100 = int(data['n_100'])
        if int(data['n_100'])>0:
            profshow_bill.intake += int(data['n_100'])*100
        else:
            profshow_bill.outtake -= int(data['n_100'])*100
        profshow_bill.n50 = int(data['n_50'])
        if int(data['n_50'])>0:
            profshow_bill.intake += int(data['n_50'])*50
        else:
            profshow_bill.outtake -= int(data['n_50'])*50
        profshow_bill.n20 = int(data['n_20'])
        if int(data['n_20'])>0:
            profshow_bill.intake += int(data['n_20'])*20
        else:
            profshow_bill.outtake -= int(data['n_20'])*20
        profshow_bill.n10 = int(data['n_10'])
        if int(data['n_10'])>0:
            profshow_bill.intake += int(data['n_10'])*10
        else:
            profshow_bill.outtake -= int(data['n_10'])*10
        profshow_bill.amount = profshow_bill.intake - profshow_bill.outtake
        profshow_bill.created_by = data['created_by']
        profshow_bill.save()
        try:
            bits_id = data['bits_id']
            if not bits_id == '':
                if not re.match(r'[h,f]\d{6}', bits_id):
                    context = {
                        'error_heading':'No match found',
                        'message':'Bitsian does not exist.',
                        'url':request.build_absolute_uri(reverse('messportal:index'))
                        }
                    profshow_bill.delete()
                    return render(request, 'registrations/message.html', context)
                profshow_bill.bits_id = bits_id
                profshow_bill.save()
        except:
            pass 
        barcode = 'oasis17' + data['barcode']
        try:
            participant = Participant.objects.get(barcode=barcode)
        except:
            context = {
                'error_heading':'No match found',
                'message':'Participant does not exist.',
                'url':request.build_absolute_uri(reverse('messportal:index'))
            }
            profshow_bill.delete()
            return render(request, 'registrations/message.html', context)
        
        if prof_show.price == 850:
            id_list = [6, 7]
            prof_shows = ProfShow.objects.filter(id__in=id_list)
            for prof_show in prof_shows:
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
        
        else:
            try:
                attendance = Attendance.objects.get(participant=participant, prof_show=prof_show)
                attendance.count += int(data['count'])
                attendance.save()
            except:
                attendance = Attendance()
                attendance.participant = participant
                attendance.prof_show = prof_show
                attendance.paid = True
                attendance.count = int(data['count'])
                attendance.save()
            
        return redirect(reverse('messportal:view_all_profshow_bills'))
    prof_shows = ProfShow.objects.all()
    return render(request, 'messportal/create_profshow_bill.html', {'prof_shows':prof_shows})

@staff_member_required
def view_all_mess_bills(request):
    rows = [{'data':[bill.created_time, bill.created_by, bill.amount, bill.quantity, bill.item.name, bill.item.price,bill.mess,Participant.objects.get(barcode=bill.buyer_id).name], 'link':[{'title':'View Details', 'url':request.build_absolute_uri(reverse('messportal:mess_bill_details', kwargs={'mb_id':bill.id}))}]} for bill in MessBill.objects.all()]
    headings = ['Created Time', 'Created By', 'Amount', 'Quantity', 'Item', 'Price/item','Mess', 'Participant Name', 'View Details']
    title = 'Mess Bill Details'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'messportal/tables.html', {'tables':[table,]})

@staff_member_required
def view_all_profshow_bills(request):
    rows = [{'data':[bill.created_time, bill.created_by, bill.amount, bill.quantity, bill.prof_show.name, bill.prof_show.price,Participant.objects.get(barcode=bill.buyer_id).name, get_bits_id(bill)], 'link':[{'title':'View Details', 'url':request.build_absolute_uri(reverse('messportal:profshow_bill_details', kwargs={'ps_id':bill.id}))}]} for bill in ProfShowBill.objects.all()]
    headings = ['Created Time', 'Created By', 'Amount', 'Quantity', 'Prof Show', 'Price/profshow','Participant Name', 'Bits ID','View Details',]
    title = 'Prof Show Bill Details'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    rows = [{'data':[bill.created_time, bill.created_by, bill.quantity, bill.prof_show.name, bill.prof_show.price,Bitsian.objects.filter(ems_code=bill.buyer_id)[0].name], 'link':[]} for bill in BitsProfShowBill.objects.all()]
    headings = ['Created Time', 'Created By', 'Quantity', 'Prof Show', 'Price/profshow','Bitsian Name',]
    title = 'Prof Show Bill Details-Bitsians'
    table2 = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'messportal/tables.html', {'tables':[table, table2]})

def get_bits_id(bill):
    if bill.bits_id:
        return bill.bits_id
    else:
        return ''

@staff_member_required
def mess_bill_details(request, mb_id):
    bill = get_object_or_404(MessBill, id=mb_id)
    participant = Participant.objects.get(barcode = bill.buyer_id)
    return render(request, 'messportal/bill_details.html', {'bill':bill, 'mess':True, 'participant':participant})

@staff_member_required
def profshow_bill_details(request, ps_id):
    bill = get_object_or_404(ProfShowBill, id=ps_id)
    try:
        participant = Participant.objects.get(barcode = bill.buyer_id)
    except:
        participant = None
    try:
        bitsian = Bitsian.objects.get(ems_code=bill.buyer_id)
    except:
        bitsian = None
    return render(request, 'messportal/bill_details.html', {'bill':bill, 'profshow':True, 'participant':participant, 'bitsian':bitsian})

@staff_member_required
def mess_bill_receipt(request, mb_id):
    from datetime import datetime
    bill = get_object_or_404(MessBill, id=mb_id)
    participant = Participant.objects.get(barcode = bill.buyer_id)
    time = datetime.now()
    return render(request, 'messportal/thermal_receipt.html', {'bill':bill, 'mess':True, 'participant':participant, 'time':time,})

@staff_member_required
def profshow_bill_receipt(request, ps_id):
    from datetime import datetime
    bill = get_object_or_404(ProfShowBill, id=ps_id)
    participant = Participant.objects.get(barcode = bill.buyer_id)
    time = datetime.now()
    return render(request, 'messportal/bill_receipt.html', {'bill':bill, 'profshow':True, 'participant':participant, 'time':time, })

@staff_member_required
def delete_mess_bill(request, mb_id):
    mess_bill = get_object_or_404(MessBill, id=mb_id)
    mess_bill.delete()
    return redirect(reverse('messportal:view_all_mess_bills'))

@staff_member_required
def delete_profshow_bill(request, ps_id):
    profshow_bill = get_object_or_404(ProfShowBill, id=ps_id)
    participant = Participant.objects.get(barcode=profshow_bill.buyer_id)
    prof_show = profshow_bill.prof_show
    attendance = Attendance.objects.get(participant=participant, prof_show=prof_show)
    attendance.count -= profshow_bill.quantity
    attendance.save()
    profshow_bill.delete()
    return redirect(reverse('messportal:view_all_profshow_bills'))