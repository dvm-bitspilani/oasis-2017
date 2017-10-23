from django.contrib import admin

from .models import *
    
admin.site.register(Bill)
admin.site.register(Bhavan)
admin.site.register(Room)
admin.site.register(Note)