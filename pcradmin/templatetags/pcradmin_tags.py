from django import template
from registrations.models import *
from events.models import *
from functools import reduce
from django.db.models import Q
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
    paid = Participant.objects.filter(Q(paid=True,controlz_paid=False) | Q(curr_paid=True, curr_controlz_paid=False)).count()
    full_paid = Participant.objects.filter(Q(paid=True,controlz_paid=True) | Q(curr_paid=True, curr_controlz_paid=True)).count()
    pcr_final = Participant.objects.filter(pcr_final=True).count()
    return {'email_verified':email_verified, 'cr_approved':cr_approved, 'pcr_approved':pcr_approved, 'paid':paid, 'full_paid':full_paid, 'pcr_final':pcr_final}


@register.simple_tag
def is_profile_complete(part):
    try:
        profile_url = part.profile_pic.url
        docs_url = part.verify_docs.url
        return True
    except:
        return False