from django.contrib import admin
from .models import *

admin.site.register(Participation)
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(ProfShow)
admin.site.register(Attendance)