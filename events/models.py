from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField
from ems.models import Team, Judge, ClubDepartment, Level, Parameter, Score
from registrations.models import *

class Category(models.Model):
	
	name = models.CharField(max_length=100, unique=True)
	
	class Meta:
		
		verbose_name_plural = 'Categories'
	
	def __unicode__(self):
		return self.name

class Event(models.Model):
	
	name = models.CharField(max_length=100,unique=True)
	content = RichTextField()
	appcontent = models.TextField(max_length=3000, default='')
	short_description = models.CharField(blank=True,max_length=140)
	rules = models.CharField(blank=True,max_length=200)
	detail_rules = models.TextField(max_length=3000,default='', null=True, blank=True)
	category = models.ForeignKey('Category', default=3)
	is_kernel = models.BooleanField(default=False)
	icon = models.ImageField(blank=True, upload_to="icons")
	date = models.CharField(max_length=100, default='TBA')
	time = models.CharField(max_length=100, default='TBA')
	venue = models.CharField(max_length=100, default='TBA')
	min_team_size = models.IntegerField(default=0)
	max_team_size = models.IntegerField(default=0)
	min_teams = models.IntegerField(default=0)
	max_teams = models.IntegerField(default=0)
	contact = models.CharField(max_length=140, default='')

	def __unicode__(self):
		return self.name

class Participation(models.Model):

	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	participant = models.ForeignKey('registrations.Participant', on_delete=models.CASCADE, null=True)
	pcr_approved = models.BooleanField(default=False)
	cr_approved = models.BooleanField(default=False)

	def __unicode__(self):	
		return str(self.event.name)+'-'+str(self.participant.name)

class ProfShow(models.Model):

	name = models.CharField(max_length=100,unique=True)
	appcontent = models.TextField(max_length=3000, default='')
	short_description = models.CharField(blank=True,max_length=140)
	date = models.CharField(max_length=100, default='TBA')
	time = models.CharField(max_length=100, default='TBA')
	venue = models.CharField(max_length=100, default='TBA')
	contact = models.CharField(max_length=140, default='')
	price = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name + '-prof show'

class Attendance(models.Model):

	prof_show = models.ForeignKey(ProfShow, on_delete=models.CASCADE)
	participant = models.ForeignKey('registrations.Participant', on_delete=models.CASCADE, null=True)
	paid = models.BooleanField(default=False)
	attended = models.BooleanField(default=False)
	count = models.IntegerField(default=0)
	passed_count = models.IntegerField(default=0)
	bitsian = models.ForeignKey('ems.Bitsian', on_delete=models.CASCADE, null=True)

	def __unicode__(self):
		return str(self.prof_show.name)