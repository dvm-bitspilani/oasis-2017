from django.shortcuts import render, redirect, reverse
from django.contrib.admin.views.decorators import staff_member_required
from registrations.models import *
from events.models import *
from .models import *

def index(request):
    if request.user.is_authenticated():
        if request.user.is_staff:
            return <events-edit>
        else:
            return <event-select>
    else:
        return redirect(reverse('ems:login'))


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                
                return HttpResponseRedirect(reverse('registrations:index'))
            else:
                context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional Contacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .'}
                return render({request, 'ems/message.html', 'context':context})
        else:
            context = {'error_heading' : "Invalid Login Credentials", 'message' :  'Invalid Login Credentials. Please try again'}
            return render({request, 'ems/message.html', 'context':context})

    else:
        return render(request, 'ems/login.html')

