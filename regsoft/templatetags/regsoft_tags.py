from django import template
from registrations.models import *
from events.models import *
from functools import reduce
from django.db.models import Q
register = template.Library()

@register.inclusion_tag('regsoft/show_tags.html')
def show_tags():
    pcr_final = Participant.objects.filter(pcr_final=True).count()
    firewallz = Participant.objects.filter(firewallz_passed=True).count()
    controlz = Participant.objects.filter(Q(paid=True,controlz_paid=True) | Q(curr_paid=True, curr_controlz_paid=True)).count()
    recnacc = Participant.objects.filter(acco=True).count()
    return {'pcr_final':pcr_final, 'firewallz':firewallz, 'controlz':controlz, 'recnacc':recnacc}

@register.simple_tag
def navbar_color(name):
    username = name
    if 'firewallz' == username:
        return 'cyan'
    if 'controlz' == username:
        return 'orange'
    if 'recnacc' == username:
        return 'light-green'
    else:
        return 'blue'

@register.filter
def get_events_list(participant):
    participation_set = Participation.objects.filter(participant=participant, pcr_approved=True)
    events = ''
    for participation in participation_set:
        events += participation.event.name + ', '
    events = events[:-2]
    return events

@register.filter
def participant_count(group):
    return group.participant_set.all().count()

@register.filter
def get_gleader_name(group):
    return group.participant_set.get(is_g_leader=True).name

