from __future__ import unicode_literals

from django.db import models
from registrations.models import *
from events.models import *
from django.contrib.auth.models import *

class Team(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField('Participant')
    leader = models.OneToOneField('Participant', related_name='team_leader')
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=0)
    is_winner = models.BooleanField(default=False)
    is_finalist = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name