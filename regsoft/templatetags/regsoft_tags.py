from django import template
from registrations.models import *
from events.models import *
from functools import reduce
from django.db.models import Q
register = template.Library()

@register.inclusion_tag('pcradmin/show_tags.html')
def show_tags():
    pcr_final = Participant.objects.filter(pcr_final=True).count()
    firewallz = Participant.objects.filter(firewallz_approved=True).count()
    controlz = Participant.objects.filter(Q(paid=True,controlz_paid=True) | Q(curr_paid=True, curr_controlz_paid=True)).count()
    recnacc = Participant.objects.filter(acco=True).count()
    return {'pcr_final':pcr_final, 'firewallz':firewallz, 'controlz':controlz, 'recnacc':recnacc}