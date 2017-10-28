from __future__ import unicode_literals

from django.db import models
from events.models import *
from registrations.models import *
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=200, default='')
    members = models.ManyToManyField('registrations.Participant')
    leader = models.ForeignKey('registrations.Participant', related_name='team_leader', null=True)
    members_bitsian = models.ManyToManyField('ems.Bitsian')
    leader_bitsian = models.ForeignKey('ems.Bitsian', related_name='bitsian_leader', null=True)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, null=True)
    rank = models.PositiveSmallIntegerField(default=0)
    is_winner = models.BooleanField(default=False)
    is_finalist = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return self.name

class ClubDepartment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    co_ordinator = models.CharField(max_length=200)
    phone = models.BigIntegerField(default=0)
    email_id = models.EmailField()
    events = models.ManyToManyField('events.Event', blank=True)
    profshows = models.ManyToManyField('events.ProfShow')

    def __unicode__(self):
        return self.name + '-' + self.co_ordinator

class Judge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, default='')
    level = models.ForeignKey('ems.Level', null=True, blank=True)
    left_the_event = models.BooleanField(default=False)
    frozen = models.BooleanField(default=False)
    
    def __unicode__(self):
            return self.name

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
        return str(self.name) + '(' + str(self.max_val) + ')'

class Bitsian(models.Model):
	
    long_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    ems_code = models.CharField(max_length=10, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    email = models.EmailField(null=True)
    barcode = models.CharField(max_length=10, null=True, blank=True)
    bhawan = models.CharField(max_length=20, null=True, blank=True)
    room_no = models.IntegerField(default=0)
    
    def __unicode__(self):
		return str(self.long_id) + ' - '+ str(self.name)

class Score(models.Model):
    level = models.ForeignKey('ems.Level', null=True)
    team = models.ForeignKey('ems.Team', related_name='scores', null=True)
    score_card = models.CharField(max_length=500, default="{}") # eg. {judge_id1:{parameter_id1:score, parameter_id2:score},
                                                 # judge_id2:{parameter_id1:score, parameter_id2:score}}

    comments = models.TextField(default="{}") #{judge1:comment, judge2:comment}
    total_score = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return str(self.team.name) + ' - ' +str(self.level.event.name) + ' - ' + str(self.level.position)

    def get_score(self):
        return eval(self.score_card)

    # def get_score_p(self, p_id):
    #     score_dict = eval(self.score)
    #     x=0
    #     for i in score_dict:
    #         x+=score_dict[i][p_id]
    #     return x

    def get_score_j(self, j_id):
        score_dict = eval(self.score_card)
        return score_dict[j_id]

    def get_total_j(self, j_id):
        score_dict = eval(self.score_card)[j_id]
        return sum(score_dict.values())
    
    def get_score_j_p(self, j_id, p_id):
        score_dict = eval(self.score_card)
        return score_dict[j_id][p_id]

    def save(self, *args, **kwargs):
        parameters = self.level.parameter_set.all()
        judges = self.level.judge_set.all()
        score_str = self.score_card
        comment_str = self.comments
        if not comment_str:
            comment_dict = {}
        else:
            comment_dict = eval(comment_str)
        if not score_str:
            score = {}
        else:
            score = eval(score_str)
        for j in judges:
            comment_dict.setdefault(j.id, '')
            score.setdefault(j.id, {})
            s = score[j.id]
            for p in parameters:
                s.setdefault(p.id, 0)
            score[j.id] = s
        self.score_card = str(score)
        self.comments = str(comment_dict)
        super(Score, self).save(*args, **kwargs)

    def get_total_score(self):
        score_dict = eval(self.score_card)
        x=0

        for i in score_dict.keys():
            if not self.level.judge_set.get(id=i).left_the_event:
                x+=sum(score_dict[i].values())
        return x

    def get_comments(self):
        return eval(self.comments)

    def get_comment_j(self, j_id):
        return eval(self.comments)[j_id]