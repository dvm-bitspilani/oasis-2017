from __future__ import unicode_literals

from django.db import models
from events.models import Event


class College(models.Model):

	name = models.CharField(max_length=200, unique=True)
	is_displayed = models.BooleanField(default=True)
	
	def __unicode__(self):
		return str(self.name)

class IntroReg(models.Model):

	GENDERS = (
		('M','Male'),
		('F','Female'),
		)

	name = models.CharField(max_length=200)
	college = models.ForeignKey(College, on_delete = models.CASCADE)
	gender = models.CharField(max_length=1, choices=GENDERS)
	city = models.CharField(max_length=20)
	phone_no = models.BigIntegerField()
	email_id = models.EmailField(unique=True)
	events = models.ManyToManyField(Event, blank=True)
	#extra details
	literary = models.BooleanField(default=False)
	dance = models.BooleanField(default=False)
	music = models.BooleanField(default=False)
	theater = models.BooleanField(default=False)
	fashion_parade = models.BooleanField(default=False)
	find_out_about_oasis = models.CharField(max_length=100)
	
	def __unicode__(self):
	
		return self.name + ' ' + self.college