from django import template
from registrations.models import *
from events.models import *
from functools import reduce
from django.db.models import Q
from ems.models import *
register = template.Library()

@register.simple_tag
def get_events(a):
	return reduce((lambda x,y: str(x)+', '+y.name), a.events.all())