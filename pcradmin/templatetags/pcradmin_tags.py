from django import template
from registrations.models import *
from events.models import *
from functools import reduce
register = template.Library()

@register.inclusion_tag('pcradmin/show_tags.html')
def show_tags():
    email_verified = Participant.objects.filter(email_verified=True).count()
    cr_approved = 0
    for participant in Participant.objects.filter(email_verified=True):
        if Participation.objects.filter(participant=participant, cr_approved=True):
            cr_approved += 1
            continue
    pcr_approved = Participant.objects.filter(pcr_approved=True).count()
    paid = Participant.objects.filter(paid=True).count()
    return {'email_verified':email_verified, 'cr_approved':cr_approved, 'pcr_approved':pcr_approved, 'paid':paid}