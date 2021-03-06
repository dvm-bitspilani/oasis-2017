from __future__ import unicode_literals

from django.db import models
from events.models import *
from django.contrib.auth.models import User
from datetime import datetime

class College(models.Model):

	name = models.CharField(max_length=200, unique=True)
	
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
	literary = models.BooleanField(default=False)
	dance = models.BooleanField(default=False)
	music = models.BooleanField(default=False)
	theater = models.BooleanField(default=False)
	fashion_parade = models.BooleanField(default=False)
	find_out_about_oasis = models.CharField(max_length=100)
	
	def __unicode__(self):
	
		return self.name + ' ' + self.college

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class PaymentGroup(models.Model):

	amount_paid = models.IntegerField(default=0)
	created_time = models.DateTimeField(auto_now=True)

class EmailGroup(models.Model):
	created_time = models.DateTimeField(auto_now=True)

class Participant(models.Model):

	GENDERS = (
		('M','Male'),
		('F','Female'),
		)

	name = models.CharField(max_length=200)
	barcode = models.CharField(max_length=50, null=True)
	email = models.EmailField(unique=True)
	college = models.ForeignKey(College, on_delete=None, null=True)
	city = models.CharField(max_length=100, null=True)
	state = models.CharField(max_length=50)
	phone = models.BigIntegerField()
	gender = models.CharField(max_length=10, choices=GENDERS)
	year_of_study = models.CharField(max_length=3, null=True)
	head_of_society = models.BooleanField(default=False)
	user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
	profile_pic = models.ImageField(upload_to=user_directory_path, null=True)
	verify_docs = models.ImageField(upload_to=user_directory_path, null=True, default=None)
	email_verified = models.BooleanField(default=False)
	email_token = models.CharField(max_length=32, null=True, blank=True)
	is_cr = models.BooleanField(default=False)
	pcr_approved = models.BooleanField(default=False)
	paid = models.BooleanField(default=False)
	payment_group = models.ForeignKey(PaymentGroup, on_delete=models.SET_NULL, null=True)
	pcr_final = models.BooleanField(default=False)
	email_group = models.ForeignKey(EmailGroup, on_delete=models.SET_NULL, null=True)
	firewallz_passed = models.BooleanField(default=False)
	group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True)
	acco = models.BooleanField(default=False)
	room = models.ForeignKey('regsoft.Room', null=True, blank=True)
	controlz = models.BooleanField('controlz passed', default=False)
	controlz_paid = models.BooleanField(default=False)
	curr_paid = models.BooleanField(default=False)
	curr_controlz_paid = models.BooleanField(default=False)
	bill = models.ForeignKey('regsoft.Bill' ,null=True, on_delete=models.SET_NULL)
	recnacc_time = models.DateTimeField(null=True, auto_now=False)
	is_g_leader = models.BooleanField(default=False)
	events = models.ManyToManyField(Event, through=Participation)
	cr_approved = models.BooleanField(default=False)
	checkout_group = models.ForeignKey('CheckoutGroup', on_delete=models.SET_NULL, null=True)
	ems_code = models.CharField(max_length=10, default='', null=True)
	is_guest = models.BooleanField(default=False)
	bits_id = models.CharField(max_length=20, null=True, blank=True)

	def __unicode__(self):
		return (self.name) + ' - ' + str(self.college.name)

class Group(models.Model):

	amount_deduct = models.IntegerField(default=0)
	created_time = models.DateTimeField(auto_now=True)
	group_code = models.CharField(max_length=100, null=True, blank=True)

class CheckoutGroup(models.Model):

	amount_retained = models.IntegerField(default=0)
	created_time = models.DateTimeField(auto_now=True)
	group_code = models.CharField(max_length=100, null=True, blank=True)


class Bitsian(models.Model):
	
	long_id = models.CharField(max_length=20, null=True, blank=True)
	name = models.CharField(max_length=50, null=True, blank=True)
	gender = models.CharField(max_length=1, null=True, blank=True)
	email = models.EmailField(null=True)
	barcode = models.CharField(max_length=10, null=True, blank=True, unique=True)
	phone = models.BigIntegerField(default=0, null=True)
	bhawan = models.CharField(max_length=20, null=True, blank=True)
	room_no = models.IntegerField(default=0)
	user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)

	def __unicode__(self):
		return self.long_id + ' - '+ self.name