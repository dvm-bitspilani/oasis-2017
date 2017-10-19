from django import template
from registrations.models import *
from events.models import *
from functools import reduce
from django.db.models import Q
register = template.Library()

@register.inclusion_tag('pcradmin/show_tags.html')
def show_tags():
    mess_bills = MessBill.objects.all.count()
    profshow_bills = ProfShowBill.objects.all().count()
    return {'mess_bills':mess_bills, 'profshow_bills':profshow_bills}