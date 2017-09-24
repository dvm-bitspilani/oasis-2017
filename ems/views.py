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


