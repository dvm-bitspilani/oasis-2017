from __future__ import unicode_literals

from django.db import models
from events.models import *
from registrations.models import *

# class Team(models.Model):
#     name = models.CharField(max_length=100)


class Team(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField('registrations.Participant')
    leader = models.OneToOneField('registrations.Participant', related_name='team_leader')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=0)
    is_winner = models.BooleanField(default=False)
    is_finalist = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class ClubDepartment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    co_ordinator = models.CharField(max_length=200)
    phone = models.BigIntegerField(default=0)
    email_id = models.EmailField()
    events = models.ManyToManyField('events.Event', null=True, blank=True)
    
    
    def __unicode__(self):
        return self.name + '-' + self.co_ordinator

class Judge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    event = models.ForeignKey('events.Event', null=True, blank=True)

    def __unicode__(self):
        return self.name + '-' + self.event.name 

class Level(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    judges = models.ManyToManyField(Judge, blank=True, null=True)
    name = models.CharField(max_length=20)
    teams = models.ManyToManyField(Team, related_name='levels',blank=True)

    def __unicode__(self):
        return self.name + '-' + self.event.name


class Label(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    var1name = models.CharField(max_length=20, null=True, blank=True)
    var1max = models.IntegerField(default=10, null=True, blank=True)
    var2name = models.CharField(max_length=20, null=True, blank=True)
    var2max = models.IntegerField(default=10, null=True, blank=True)
    var3name = models.CharField(max_length=20, null=True, blank=True)
    var3max = models.IntegerField(default=10, null=True, blank=True)
    var4name = models.CharField(max_length=20, null=True, blank=True)
    var4max = models.IntegerField(default=10, null=True, blank=True)
    var5name = models.CharField(max_length=20, null=True, blank=True)
    var5max = models.IntegerField(default=10, null=True, blank=True)
    var6name = models.CharField(max_length=20, null=True, blank=True)
    var6max = models.IntegerField(default=10, null=True, blank=True)
    var7name = models.CharField(max_length=20, null=True, blank=True)
    var7max = models.IntegerField(default=10, null=True, blank=True)
    var8name = models.CharField(max_length=20, null=True, blank=True)
    var8max = models.IntegerField(default=10, null=True, blank=True)
    var9name = models.CharField(max_length=20, null=True, blank=True)
    var9max = models.IntegerField(default=10, null=True, blank=True)
    var10name = models.CharField(max_length=20, null=True, blank=True)
    var10max = models.IntegerField(default=10, null=True, blank=True)

    def __unicode__(self):
        return self.level.event.name + '-' + str(self.id)