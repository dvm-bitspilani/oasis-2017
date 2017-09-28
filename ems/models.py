from __future__ import unicode_literals

from django.db import models
from events.models import *
from registrations.models import *

# class Team(models.Model):
#     name = models.CharField(max_length=100)


class Team(models.Model):
    name = models.CharField(max_length=200, default='')
    members = models.ManyToManyField('registrations.Participant')
    leader = models.OneToOneField('registrations.Participant', related_name='team_leader', null=True)
    members_bitsian = models.ManyToManyField('ems.Bitsian')
    leader_bitsian = models.OneToOneField('ems.Bitsian', related_name='bitsian_leader', null=True)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=0)
    is_winner = models.BooleanField(default=False)
    is_finalist = models.BooleanField(default=False)
    is_bitsian = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return self.name

class ClubDepartment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    co_ordinator = models.CharField(max_length=200)
    phone = models.BigIntegerField(default=0)
    email_id = models.EmailField()
    events = models.ManyToManyField('events.Event', blank=True)
    
    
    def __unicode__(self):
        return self.name + '-' + self.co_ordinator

class Judge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='')
    event = models.ForeignKey('events.Event', null=True, blank=True)

    def __unicode__(self):
        return self.name + '-' + self.event.name 

class Level(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='')
    teams = models.ManyToManyField(Team, related_name='levels',blank=True)
    position = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return self.name + '-' + self.event.name


class Parameter(models.Model):
    level = models.ForeignKey(Level, null=True)
    name = models.CharField(max_length=20, default='')
    max_val = models.IntegerField(default=0)

    def __unicode__(self):
        return self.level.event.name + '-' + self.name

class Bitsian(models.Model):
	
    long_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
		return str(self.long_id) + str(self.name)

class Score(models.Model):
    is_frozen = models.BooleanField(default=False)
    level = models.ForeignKey('ems.Level', null=True)
    team = models.ForeignKey('ems.Team', related_name='scores', null=True)
    score = models.CharField(max_length=500, default="{}") # dictionary with keys related to Parameter's id and values to score in that parameter
    total_score = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return str(self.team.name) + ' - ' +str(self.level.event.name) + ' - ' + str(self.level.position)

    def get_socre(self):
        return eval(self.score)

    def get_score_p(self, p_id):
        return eval(self.score)[p_id]

    def save(self):
        parameters = self.level.parameter_set.all()
        socre_str = self.score
        if score_str == None:
            score = {}
        else:
            score = eval(score_str)
        for p in parameters:
            score.setdefault(p.id,0)
        self.score = str(score)
        super(Score, self).save(*args, **kwargs)

    def get_total_score(self):
        return sum(eval(self.score).values())

