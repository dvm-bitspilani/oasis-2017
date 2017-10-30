from django.contrib import admin

# Register your models here.
from registrations.models import *
from events.models import Event

admin.site.register(College)
admin.site.register(IntroReg)
admin.site.register(PaymentGroup)
admin.site.register(Group)

class ParticipantAdmin(admin.ModelAdmin):
	search_fields = ['name', 'college__name']

admin.site.register(Participant, ParticipantAdmin)