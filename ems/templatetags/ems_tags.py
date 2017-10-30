from django import template
from registrations.models import *
from events.models import *
from functools import reduce
from django.db.models import Q
from ems.models import *
register = template.Library()

@register.simple_tag
def get_events(a):
	return reduce((lambda x,y: str(x)+', '+y.name), a.events.all(), '')

@register.filter
def ems_judge(request):
	user = request.user
	try:
		judge = Judge.objects.get(user=user)
		return True
	except:
		return False

@register.filter
def ems_levels(request):
	user = request.user
	try:
		judge = Judge.objects.get(user=user)
		levels = Level.objects.filter(event=judge.event)
		return levels
	except:
		return []

@register.simple_tag
def get_it(value, arg):
	return value[arg]	