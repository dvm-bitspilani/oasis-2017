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
    created_time = models.DateTimeField(auto_now=True)
    buyer_id = models.CharField(max_length=10)
    quantity = models.IntegerField(default=0)
    mess = models.CharField(max_length=10)
    n2000 = models.IntegerField(default=0)
    n500 = models.IntegerField(default=0)
    n200 = models.IntegerField(default=0)
    n100 = models.IntegerField(default=0)
    n50 = models.IntegerField(default=0)
    n20 = models.IntegerField(default=0)
    n10 = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    intake = models.IntegerField(default=0)
    outtake = models.IntegerField(default=0)
    created_by = models.CharField(max_length=50)

    def __unicode__(self):
        return 'mess-'+ self.buyer_id + '-' + str(self.amount)

class ProfShowBill(models.Model):
    prof_show = models.ForeignKey('events.ProfShow', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=True)
    buyer_id = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    n2000 = models.IntegerField(default=0)
    n500 = models.IntegerField(default=0)
    n200 = models.IntegerField(default=0)
    n100 = models.IntegerField(default=0)
    n50 = models.IntegerField(default=0)
    n20 = models.IntegerField(default=0)
    n10 = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    intake = models.IntegerField(default=0)
    outtake = models.IntegerField(default=0)
    created_by = models.CharField(max_length=50)

    def __unicode__(self):
        return 'profshow-' + self.buyer_id + '-' + str(self.amount)