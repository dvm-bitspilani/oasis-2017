from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

class Player(models.Model):
	email = models.EmailField(unique=True)
	phone = models.BigIntegerField()
	score = models.IntegerField(default=0)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	day1 = models.IntegerField(default=0)
	day2 = models.IntegerField(default=0)
	day3 = models.IntegerField(default=0)

	def __unicode__(self):
		return str(self.name) + ' ' + str(self.email)


class Day(models.Model):
	day_no = models.IntegerField(default=0)
	is_active = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.day_no)


class Question(models.Model):
	image = models.CharField(max_length=60,default='')
	question_no = models.IntegerField(default=0)
	day = models.ForeignKey(Day)
	answer = models.CharField(max_length=100)
	points = models.IntegerField(default=0)

	def __unicode__(self):
		return 'Question no. : ' + str(self.question_no) + ' Day : ' + str(self.day)
