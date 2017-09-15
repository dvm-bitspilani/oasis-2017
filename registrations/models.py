from __future__ import unicode_literals

from django.db import models
from events.models import *
from django.contrib.auth.models import User

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

class GroupLeader(models.Model):

	GENDERS = (

			('M', 'MALE'),
			('F', 'FEMALE'),
		)
	
	name = models.CharField(max_length=200)
	college = models.ForeignKey(College, on_delete=None)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=50)
	phone = models.BigIntegerField()
	email = models.EmailField(unique=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
	gender = models.CharField(max_length=10, choices=GENDERS)
	events = models.ManyToManyField(Event, through=Participation) #events.models
	email_verified = models.BooleanField(default=False)
	email_token = models.CharField(max_length=32, null=True, blank=True)
	pcr_approved = models.BooleanField(default=False)
	barcode = models.CharField(max_length=50, null=True)
	
	def __unicode__(self):

		return self.name + ' ' + self.college

	class Meta:

		verbose_name_plural = 'Group Leaders'
	
class Captain(models.Model):

	GENDERS = (

			('M', 'MALE'),
			('F', 'FEMALE'),
	)

	name = models.CharField(max_length=200)
	email = models.EmailField()
	phone = models.BigIntegerField(default=0)
	event = models.ForeignKey(Event, on_delete=models.CASCADE, default=None)
	g_leader = models.ForeignKey(GroupLeader, on_delete=models.CASCADE, default=None)
	coach = models.CharField(max_length=200)
	paid = models.BooleanField(default=False)
	is_single = models.NullBooleanField()
	total_players = models.IntegerField(default=1)
	gender = models.CharField(max_length=10, choices=GENDERS)
	barcode = models.CharField(max_length=50, null=True)
	pcr_final = models.BooleanField(default=False)

	def __unicode__(self):

		return self.name + '-' + str(self.g_leader.college.name)

	class Meta:

		verbose_name_plural = 'Team Captains'

class Participant(models.Model):

	name = models.CharField(max_length=200)
	is_captain = models.BooleanField(default=False)
	captain = models.ForeignKey(Captain, on_delete=models.CASCADE)
	email = models.EmailField()
	firewallz_passed = models.BooleanField(default=False)
	room = models.ForeignKey('regsoft.Room', null=True, blank=True)
	controlz = models.BooleanField('controlz passed', default=False)
	barcode = models.CharField(max_length=50, null=True)
	bill = models.ForeignKey('regsoft.Bill' ,null=True, on_delete=None)
	recnacc_time = models.DateTimeField(null=True, auto_now=False)

	def __unicode__(self):
		return (self.name) + ' ' + str(self.captain.g_leader.college.name) + str(self.captain.event.name) 