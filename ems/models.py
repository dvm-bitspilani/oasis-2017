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
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name + '-' + self.event.name


class Label(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.level.event.name + '-' + str(self.id)

class Parameter(models.Model):
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)
    max_val = models.IntegerField(default=0)

    def __unicode__(self):
        return self.level.event.name + '-' + self.name

class Bitsian(models.Model):
    GENDERS = (
		('M', 'Male'),
		('F', 'Female'),)
	
    long_id = models.CharField(max_length=20, null=True, blank=True)
    short_id = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDERS, null=True, blank=True)
    college = models.CharField(max_length=200, default='BITS Pilani', null=True, blank=True)
	
    def __unicode__(self):
		return str(self.name)