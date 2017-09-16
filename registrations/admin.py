from django.contrib import admin

# Register your models here.
from registrations.models import *
from events.models import Event

admin.site.register(College)
admin.site.register(Participant)
admin.site.register(IntroReg)
