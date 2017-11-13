from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse
from .models import *
from registrations.models import *
from events.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
import sendgrid
import os
from sendgrid.helpers.mail import *
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo
import sendgrid
import re
from sendgrid.helpers.mail import *
from oasis2017.keyconfig import *
from django.contrib.auth.models import User
import string
from random import sample, choice
from django.contrib import messages
from django.db.models import Q
import requests
from ems.models import *
chars = string.letters + string.digits

try:
	from oasis2017.config import *
	api = Instamojo(api_key=INSTA_API_KEY, auth_token=AUTH_TOKEN)
except:
	api = Instamojo(api_key=INSTA_API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/') #when in development

@staff_member_required
def index(request):
    return redirect(reverse('store:create_cart'))

@staff_member_required
def create_cart(request):
    if request.method == 'POST':
        data = request.POST
        cart = Cart()
        buyer_id = data['buyer_id']
        cart.buyer_id = buyer_id
        if re.match(r'oasis17\w{8}', buyer_id):
            try:
                part = Participant.objects.get(barcode=buyer_id)
                cart.participant = part
                cart.email = part.email
            except:
                messages.warning(request, 'Invalid participant barcode')
                return redirect(reverse('store:create_cart'))
        elif re.match(r'[h,f,p]\d{6}', buyer_id):
            cart.is_bitsian = True
            try:
                bitsian = Bitsian.objects.filter(ems_code=buyer_id)[0]
                cart.email = bitsian.email
            except:
                messages.warning(request, 'Invalid bitsian code')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Invalid codes entered')
            return redirect(request.META.get('HTTP_REFERER'))
        cart.save()
        return redirect(reverse('store:cart_details', kwargs={'c_id':cart.id}))
    else:
        carts = Cart.objects.all()
        return render(request, 'store/create_cart.html', {'carts':carts})

@staff_member_required
def cart_details(request, c_id):
    cart = get_object_or_404(Cart, id=c_id)
    added_items = Sale.objects.filter(cart=cart)
    if request.method == 'POST':
        if cart.paid:
            context = {
                'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id})),
                'error_heading': "Operation Denied",
                'message': "Sorry! Payment has been done.",
            }
            return render(request, 'registrations/message.html', context)
        data = request.POST
        sale_list = Sale.objects.filter(id__in=data.getlist('sale_list'))
        combo_list = MainCombo.objects.filter(id__in=data.getlist('combo_list'))
        for sale in sale_list:
            cart.amount -= ((sale.quantity)*(sale.item.item.price))
            mainitem = sale.item
            mainitem.quantity_left += sale.quantity
            mainitem.save()
            cart.save()
            sale.delete()
        for combo in combo_list:
            cart.amount -= (combo.combo.price)
            cart.save()
            for mainitem in combo.mainitems.all():
                mainitem.quantity_left += 1
                mainitem.save()
            combo.delete()
    sales = Sale.objects.filter(cart=cart)
    maincombos = cart.maincombos.all()
    present_items = []
    for sale in sales:
        if sale.item.item not in present_items:
            present_items.append(sale.item.item)
    unadded_items = [item for item in Item.objects.all() if item not in present_items]
    added_items = sales
    combos = Combo.objects.all()
    return render(request, 'store/cart_details.html', {'cart':cart, 'added_items':added_items, 'unadded_items':unadded_items, 'maincombos':maincombos, 'combos':combos,})

@staff_member_required
def item_details(request, c_id, i_id):
    cart = get_object_or_404(Cart, id=c_id)
    base_item = get_object_or_404(Item, id=i_id)
    main_items = base_item.mainitem_set.all()
    sale_list = []
    main_list = []
    for item in main_items:
        try:
            sale = Sale.objects.get(cart=cart, item=item)
            sale_list.append(sale)
        except:
            main_list.append(item)
    print sale_list
    print main_list
    return render(request, 'store/item_details.html', {'cart':cart, 'item':base_item, 'sale_list':sale_list, 'main_list':main_list})

@staff_member_required
def add_item(request, c_id, i_id):
    if request.method == 'POST':
        data = request.POST
        cart = get_object_or_404(Cart, id=c_id)
        if cart.paid:
            context = {
                'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id})),
                'error_heading': "Operation Denied",
                'message': "Sorry! Payment has been done.",
            }
            return render(request, 'registrations/message.html', context)
        item = get_object_or_404(Item, id=i_id)
        main_items = item.mainitem_set.all()
        sale_list = []
        main_list = []
        for item in main_items:
            try:
                sale = Sale.objects.get(cart=cart, item=item)
                sale_list.append(sale)
            except:
                main_list.append(item)
        for sale in sale_list:
            try:
                quantity = data[str(sale.id)]
                quantity = int(quantity)
                if sale.item.quantity_left < quantity:
                    messages.warning(request, 'Not enough items left.')
                    return redirect(request.META.get('HTTP_REFERER'))
                sale.item.quantity_left -= (quantity - sale.quantity)
                sale.item.save()
                cart.amount += ((quantity-sale.quantity)*(sale.item.item.price))
                sale.quantity = quantity
                sale.save()
            except:
                pass
        for item in main_list:
            try:
                print item
                quantity = data[str(item.id)]
                quantity = int(quantity)
                try:
                    sale = Sale.objects.get(cart=cart, item=item)
                    if sale.item.quantity_left < quantity:
                        messages.warning(request, 'Not enough items left.')
                        return redirect(request.META.get('HTTP_REFERER'))
                    sale.item.quantity -= (quantity - sale.quantity)
                    sale.item.save()
                    sale.quantity = quantity
                    cart.amount += ((quantity-sale.quantity)*(sale.item.item.price))
                    sale.save()
                except:
                    if int(item.quantity_left) < int(quantity):
                        print item.quantity_left, quantity
                        messages.warning(request, 'Not enough items left.')
                        return redirect(request.META.get('HTTP_REFERER'))
                    if quantity>0:
                        sale = Sale.objects.create(item=item, cart=cart, quantity=quantity)
                        cart.amount += ((sale.quantity)*(sale.item.item.price))
                        sale.item.quantity_left -= quantity
                        sale.item.save()
            except:
                pass
        cart.save()
        return redirect(reverse('store:cart_details', kwargs={'c_id':cart.id}))

@staff_member_required
def combo_details(request, c_id, co_id):
    cart = get_object_or_404(Cart, id=c_id)
    combo = get_object_or_404(Combo, id=co_id)
    return render(request, 'store/combo_details.html', {'cart':cart, 'combo':combo})

@staff_member_required
def add_combo(request, c_id, co_id):
    if request.method == 'POST':
        data = request.POST
        cart = get_object_or_404(Cart, id=c_id)
        combo = get_object_or_404(Combo, id=co_id)
        maincombo = MainCombo.objects.create(combo=combo)
        for item in combo.items.all():
            size = Size.objects.get(name=data[str(item.id)])
            mainitem = MainItem.objects.get(item=item, size=size)
            maincombo.mainitems.add(mainitem)
            if mainitem.quantity_left < 1:
                messages.warning(request, 'Not enough items left.')
                maincombo.delete()
                return redirect(request.META.get('HTTP_REFERER')) 
            mainitem.quantity_left -= 1
            mainitem.save()
        cart.maincombos.add(maincombo)
        cart.amount += combo.price
        cart.save()
        return redirect(reverse('store:cart_details', kwargs={'c_id':cart.id}))

@staff_member_required
def make_cash_payment(request, c_id):
    cart = get_object_or_404(Cart, id=c_id)
    if cart.is_bitsian:
        cart.paid = True
        cart.save()
        return redirect(reverse('store:index'))
    if request.method == 'POST':
        data = request.POST
        id_list = data.getlist('data')
        bill = CartBill()
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
        if not (bill.amount == 0):
            bill.cart = cart
            bill.save()
            cart.paid = True
            cart.save()
            participant = cart.participant
            send_to = participant.email
            name = participant.name
            body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
            <center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
            <pre style="font-family:Roboto,sans-serif">
Hello %s!
Thank you for using the facility of Oasis Store.
Your payment for %s was successful. 
        </pre>
            ''' %(name, str(cart.amount))
            sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
            from_email = Email('store@bits-oasis.org')
            to_email = Email(send_to)
            subject = "Payment for Oasis Store"
            content = Content('text/html', body)

            try:
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
            except :
                context = {
                    'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id})),
                    'error_heading': "Error sending mail",
                    'message': "Sorry! Error in sending email. Please try again.",
                }
                return render(request, 'registrations/message.html', context)
            return redirect(reverse('store:show_all_bills'))
        else:
            messages.warning(request, 'Please enter a bill amount.')
            return redirect(reverse('store:make_cash_payment', kwargs={'c_id':cart.id}))
    else:
        return render(request, 'store/make_cash_payment.html', {'cart':cart})

@staff_member_required
def show_all_bills(request):
    rows = [{'data':[bill.created_time, bill.amount, bill.cart.participant.name, bill.cart.participant.college.name], 'link':[{'title':'View Details', 'url':request.build_absolute_uri(reverse('store:bill_details', kwargs={'cb_id':bill.id}))}]} for bill in CartBill.objects.all()]
    headings = ['Created Time', 'Amount', 'Participant Name', 'Participant College', 'View Details']
    title = 'Bill Details'
    table = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }

    rows = [{'data':[bill.created_time, bill.amount, get_bitsian(bill.cart).name, get_bitsian(bill.cart).long_id], 'link':[]} for bill in CartBill.objects.filter(cart__is_bitsian=True)]
    headings = ['Created Time', 'Amount', 'Bitsian Name', 'Bitsian ID',]
    title = 'Bitsian Details'
    table2 = {
        'rows':rows,
        'headings':headings,
        'title':title,
    }
    return render(request, 'store/tables.html', {'tables':[table, table2]})

def get_bitsian(cart):
    return Bitsian.objects.filter(email=cart.email)[0]

@staff_member_required
def bill_details(request, cb_id):
    bill = get_object_or_404(CartBill, id=cb_id)
    participant = bill.cart.participant
    return render(request, 'store/bill_details.html', {'bill':bill, 'participant':participant,})

@staff_member_required
def bill_receipt(request, cb_id):
    from datetime import datetime
    bill = get_object_or_404(CartBill, id=cb_id)
    participant = bill.cart.participant
    time = datetime.now()
    return render(request, 'store/bill_receipt.html', {'bill':bill,'participant':participant, 'time':time,})

@staff_member_required
def delete_bill(request, cb_id):
    bill = get_object_or_404(CartBill, id=cb_id)
    cart = bill.cart
    cart.paid = False
    cart.save()
    bill.delete()
    return redirect(reverse('store:show_all_bills'))

def generate_cart_code(cart):
    import uuid
    token = uuid.uuid4().hex
    registered_tokens = [cart.cart_token for cart in Cart.objects.all()]

    while token in registered_tokens:
        token = uuid.uuid4().hex

    cart.cart_token = token
    cart.save()
    return token

@staff_member_required
def make_online_payment(request, c_id):
    cart = get_object_or_404(Cart, id=c_id)
    if cart.is_bitsian:
        cart.paid = True
        cart.save()
        return redirect(reverse('store:index'))
    participant = cart.participant
    send_to = participant.email
    name = participant.name
    body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
    <center><img src="http://bits-oasis.org/2017/static/registrations/img/logo.png" height="150px" width="150px"></center>
    <pre style="font-family:Roboto,sans-serif">
Hello %s!
Thank you for using the facility of Oasis Store.
Click on the link below to complete the payment and avail your cart items.
<a href="%s">Pay with Instamojo.</a>
</pre>
    ''' %(name, str(request.build_absolute_uri(reverse("store:index"))) + 'payment_response/' + str(generate_cart_code(cart)) + '/')
    sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
    from_email = Email('store@bits-oasis.org')
    to_email = Email(send_to)
    subject = "Payment for Oasis Store"
    content = Content('text/html', body)

    try:
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
    except :
        context = {
            'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id})),
            'error_heading': "Error sending mail",
            'message': "Sorry! Error in sending email. Please try again.",
        }
        return render(request, 'registrations/message.html', context)

    context = {
        'error_heading': "Email sent",
        'message': "Payment URL has been sent to the participant.",
        'url':request.build_absolute_uri(reverse('store:index'))
    }
    return render(request, 'registrations/message.html', context)

def payment_response(request, token):
    cart = get_object_or_404(Cart, cart_token = token)
    amount = cart.amount
    participant = cart.participant
    name = participant.name
    email = participant.email
    phone = participant.phone
    purpose = 'Oasis Store Id :' + str(cart.id) 
    response = api.payment_request_create(buyer_name= name,
                        email= email,
                        phone= phone,
                        amount = amount,
                        purpose=purpose,
                        redirect_url= request.build_absolute_uri(reverse("store:api_request"))
                        )
    # print  email	, response['payment_request']['longurl']			
    try:
        url = response['payment_request']['longurl']
        return HttpResponseRedirect(url)
    except:
        context = {
            'error_heading': "Payment error",
            'message': "An error was encountered while processing the request. Please contact PCr, BITS, Pilani.",
            'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id}))
            }
        return render(request, 'registrations/message.html')

def api_request(request):
    import requests
    payid=str(request.GET['payment_request_id'])
    headers = {'X-Api-Key': INSTA_API_KEY,
                'X-Auth-Token': AUTH_TOKEN}
    try:
        from oasis2017 import config
        r = requests.get('https://www.instamojo.com/api/1.1/payment-requests/'+str(payid),headers=headers)
    except:
        r = requests.get('https://test.instamojo.com/api/1.1/payment-requests/'+str(payid), headers=headers)    ### when in development
    json_ob = r.json()
    if (json_ob['success']):
        payment_request = json_ob['payment_request']
        purpose = payment_request['purpose']
        amount = payment_request['amount']
        amount = int(float(amount))
        try:
            c_id = str(purpose.split(':')[1])
            cart = Cart.objects.get(id=c_id)
            cart.paid = True
            cart.save()
        except:		
            context = {
            'error_heading': "404 Not Found",
            'message': "The requested cart was not found.",
            'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id}))
            }
            return render(request, 'registrations/message.html', context)
        context = {
        'error_heading' : "Payment successful",
        'message':'Thank you for paying.',
        'url':request.build_absolute_uri(reverse('store:index'))
        }
        return render(request, 'registrations/message.html', context)

    else:

        payment_request = json_ob['payment_request']
        purpose = payment_request['purpose']
        email = payment_request['email']
        context = {
            'error_heading': "Payment error",
            'message': "An error was encountered while processing the payment. Please contact PCr, BITS, Pilani.",
            'url':request.build_absolute_uri(reverse('store:cart_details', kwargs={'c_id':cart.id}))
            }
        return render(request, 'registrations/message.html', context)