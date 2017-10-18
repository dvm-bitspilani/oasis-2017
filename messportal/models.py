from __future__ import unicode_literals

from django.db import models
from registrations.models import *
from events.models import *
from datetime import datetime

class Item(models.Model):
    name = models.CharField(max_length=30)
    price = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

class MessBill(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
