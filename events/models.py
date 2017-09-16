from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField
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
	description = models.CharField(blank=True,max_length=200)
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

	def __unicode__(self):
		return self.name

class Participation(models.Model):

	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	participant = models.ForeignKey('registrations.Participant', on_delete=models.CASCADE, null=True)
	confirmed = models.BooleanField(default=False)

	def __unicode__(self):	
		return str(self.event.name)+'-'+str(self.participant.name)
