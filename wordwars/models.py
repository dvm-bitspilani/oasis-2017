from __future__ import unicode_literals

from django.db import models

class Participant(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField(unique=True)
	phone = models.BigIntegerField()
	password = models.CharField(max_length=100)
	day = models.IntegerField(default=0)
	score = models.IntegerField(default=0)

	def __unicode__(self):
		return str(self.name) + ' ' + str(self.email)

class Question(models.Model):
	image = models.CharField(max_length=60,default='')
	question_no = models.IntegerField(default=0)
	day = models.IntegerField(default=0)
	answer = models.CharField(max_length=100)
	points = models.IntegerField(default=0)

	def __unicode__(self):
		return 'Question no. : ' + str(self.question_no) + ' Day : ' + str(self.day)