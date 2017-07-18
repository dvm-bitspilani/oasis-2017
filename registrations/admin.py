from django.contrib import admin

# Register your models here.
from registrations.models import College
from events.models import Event

admin.site.register(College)
admin.site.register(Event)