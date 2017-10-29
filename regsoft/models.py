from __future__ import unicode_literals

from django.db import models

class Bhavan(models.Model):

	name = models.CharField(max_length=30)

	def __unicode__(self):

		return self.name

class Room(models.Model):

	bhavan = models.ForeignKey(Bhavan, on_delete=models.CASCADE)
	room = models.CharField(max_length=30)
	vacancy = models.IntegerField(default=0)
	capacity = models.IntegerField(default=0)

	def __unicode__(self):

		return self.room + '-' + str(self.bhavan.name)

class Bill(models.Model):

	amount = models.IntegerField()
	time_paid = models.DateTimeField(auto_now=True)
	two_thousands = models.IntegerField(null=True, blank=True, default=0)
	five_hundreds = models.IntegerField(null=True, blank=True, default=0)
	two_hundreds = models.IntegerField(null=True, blank=True, default=0)
	hundreds = models.IntegerField(null=True, blank=True, default=0)
	fifties = models.IntegerField(null=True, blank=True, default=0)
	twenties = models.IntegerField(null=True, blank=True, default=0)
	tens = models.IntegerField(null=True, blank=True, default=0)
	draft_number = models.CharField(max_length=100, null=True, blank=True, default=None)
	draft_amount = models.IntegerField(null=True, blank=True, default=0)
	two_thousands_returned = models.IntegerField(null=True, blank=True, default=0)
	five_hundreds_returned = models.IntegerField(null=True, blank=True, default=0)
	two_hundreds_returned = models.IntegerField(null=True, blank=True, default=0)
	hundreds_returned = models.IntegerField(null=True, blank=True, default=0)
	fifties_returned = models.IntegerField(null=True, blank=True, default=0)
	twenties_returned = models.IntegerField(null=True, blank=True, default=0)
	tens_returned = models.IntegerField(null=True, blank=True, default=0)
	coaches_list = models.CharField(max_length=200, null=True, blank=True)

class Note(models.Model):

	time = models.DateTimeField(auto_now=True, null=True)
	room = models.ForeignKey(Room, on_delete=models.CASCADE)
	note = models.CharField(max_length=100)
