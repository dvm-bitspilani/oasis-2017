from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404
from registrations.models import *
from events.models import *
from .models import *
import re
from django.contrib import messages
import string
from random import choice
chars = string.letters + string.digits

login_url = reverse_lazy('ems:login')


### DECORATOR ###
def permission_for_event(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        event = get_object_or_404(Event, pk=kwargs['e_id'])
        club_dept = ClubDepartment(user=user)
        if not event in club_dept.events.all():
            url = request.build_absolute_uri(reverse_lazy('ems:events_select'))
            return render(request, 'ems/message.html',  {'error_heading':'Invalid access', 'message':'You do not have access to this page.', 'url':url})

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def permission_for_judge(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        event = get_object_or_404(Event, pk=kwargs['e_id'])
        try:
            judge = Judge.objects.get(user=user, event=event)
        except:
            return redirect('ems:index')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

### DECORATORS END ###

def index(request):
    if request.user.is_authenticated() and request.user.is_staff:
        return redirect(reverse_lazy('ems:events_select'))
    else:
        return redirect(reverse_lazy('ems:login'))


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                url = re.compile(r'next=/(\S+)')
                temp = url.search(request.get_full_path())
                if temp is not None:
                    return redirect('/'+temp.group(1))
                return HttpResponseRedirect(reverse_lazy('ems:index'))
            else:
                url = request.build_absolute_uri(reverse_lazy('ems:index'))
                context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional Contacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .', 'url':url}
                return render(request, 'ems/message.html', context)
        else:
            url = request.build_absolute_uri(reverse_lazy('ems:index'))
            context = {'error_heading' : "Invalid Login Credentials", 'message' :  'Invalid Login Credentials. Please try again', 'url':url}
            return render(request, 'ems/message.html', context)

    else:
        return render(request, 'ems/login.html')


@staff_member_required(login_url=login_url)
def events_select(request):
    if request.user.is_superuser:
        event_list = Event.objects.all()
    else:
        try:
            clubdept =  ClubDepartment.objects.get(user=request.user)
            event_list = clubdept.events.order_by('name')
        except:
            logout(request)
            return redirect(reverse_lazy('ems:index'))
    
    return render(request, 'ems/event_list.html', {'event_list':event_list})


@permission_for_event
@staff_member_required(login_url=login_url)
def event_home(request, e_id):
    event = get_object_or_404(Event, id=e_id)

    if request.method == 'POST':
        data = request.POST
        print data
        position = int(data['position'])
        try:
            level = Level.objects.get(event=event, position=position)
        except:
            messages.warning(request, 'This level does not exist. Please add it from Manage Levels tab.')
            return redirect(request.META.get('HTTP_REFERER'))
        try:
            lst = data.getlist('team_list')
            team_list = Team.objects.filter(id__in=lst)
        except:
            messages.warning(request, 'Please Select atleast 1 Team')
            return redirect(request.META.get('HTTP_REFERER'))

        if data['submit'] == 'Promote':
            try:
                next_level = Level.objects.get(event=event, position = position + 1)
            except:
                messages.warning(request, 'The next level does not exist. Please add it from Manage Levels tab.')
                return redirect(request.META.get('HTTP_REFERER'))
            for team in team_list:
                if team not in level.teams.all():
                    messages.warning(request, 'A team was not in the current level. Please add it.')
                    return redirect(request.META.get('HTTP_REFERER'))
                level.teams.remove(team)
                next_level.teams.add(team)
                team.level = position+1
                team.save()
                try:
                    score = Score.objects.get(team=team, level=next_level)
                except:
                    score = Score.objects.create(team=team, level=next_level)
        elif data['submit'] == 'Demote':
            try:
                prev_level = Level.objects.get(event=event, position = position - 1)
            except:
                messages.warning(request, 'The previous level does not exist. Please add it from Manage Levels tab.')
                return redirect(request.META.get('HTTP_REFERER'))
            for team in team_list:
                level.teams.remove(team)
                prev_level.teams.add(team)
                team.level = position-1
                team.save()
                try:
                    score = Score.objects.get(team=team, level=prev_level)
                except:
                    score = Score.objects.create(team=team, level=prev_level)
        elif "add-finalists" == data['submit']:
            teamids = request.POST.getlist('registered')
            Team.objects.filter(id__in=teamids).update(is_finalist=True)
        elif "remove-finalists" == data['submit']:
            teamids = request.POST.getlist('finalists')
            Team.objects.filter(id__in=teamids).update(is_finalist=False)
        elif "add-winners" == data['submit']:
            try:
                next_level = Level.objects.get(event=event, position = position + 1)
                messages.warning(request, 'Sorry first promote them to highest level.')
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                pass
            teamids = request.POST.getlist('registered')
            teams1 = Team.objects.filter(id__in=teamid)
            if all([t.level==position for t in teams1]):
                teams1.update(is_winner=True)
            else:
                messages.warning(request, 'Sorry first promote them to highest level.')
                return redirect(request.META.get('HTTP_REFERER'))
        elif "remove-winners" == data['submit']:
            teamids = request.POST.getlist('winners')
            Team.objects.filter(id__in=teamids).update(is_winner=False)
    levels = Level.objects.filter(event=event)
    positions = range(levels.count(),0,-1)
    tables = [{'level':p, 'teams':sorted([{'team':team, 'score':Score.objects.get(team=team, level=Level.objects.get(event=event, position=p)).get_total_score()} for team in Team.objects.filter(event=event, level=p)], key=lambda x:-x['score'])} for p in positions]
    winners = event.team_set.filter(is_winner=True)
    if winners:
        w_position = winners[0].level
        winners_list = [{'team':team, 'score':Score.objects.get(team=team, level=Level.objects.get(event=event, position=w_position)).get_total_score()} for team in winners]
    context = {'event':event,'levels':levels, 'tables':tables, 'winners':winners_list}
    return render(request, 'ems/event_home.html', context)


@permission_for_event
@staff_member_required(login_url=login_url)
def event_levels(request, e_id):
    event = get_object_or_404(Event, id=e_id)

    if request.method == 'POST':
        data = request.POST
        if data['submit'] == 'delete-level':
            try:
                l_id = data['l_id']
                level = get_object_or_404(Level, id=l_id)
            except:
                return redirect(request.META.get('HTTP_REFERER'))
            level.teams.clear()
            level.delete()
    levels = Level.objects.filter(event=event)
    context = {'event':event, 'levels':levels}
    return render(request, 'ems/event_levels.html', context)


@permission_for_event
@staff_member_required(login_url=login_url)
def event_levels_add(request, e_id):
    event = Event.objects.get(id=e_id)
    levels = Level.objects.filter(event=event)
    position = levels.count()
    if request.method == 'POST':
        data = request.POST
        try:
            name = data['name']
            if name == '':
                raise Exception
            names = data['parameters'].split('?')
            maxes = list(map(lambda x: int(x), data['values'].split('?')))
            if not len(names) == len(maxes):
                raise Exception
        except:
            messages.warning(request, 'Fill the details of the level properly')
            return redirect(request.META.get('HTTP_REFERER'))
        level = Level.objects.create(name=name, position=position+1, event=event)
        for i, n in enumerate(names):
            p=Parameter.objects.create(name=n, max_val=int(maxes[i]), level=level)
        return redirect(reverse_lazy('ems:event_levels', kwargs={'e_id':event.id}))
    context = {'event':event, 'levels':levels, 'position':position}
    return render(request, 'ems/event_levels_add.html', context)


@permission_for_event
@staff_member_required(login_url=login_url)
def add_team(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    count = Team.objects.filter(event=event).count()
    try:
        level = Level.objects.get(position=1, event=event)
    except:
        messages.warning(request, 'First add atleast one level for this event')
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST':
        data = dict(request.POST)
        print data
        try:
            teams_str = data['teams'][0]
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        print teams_str
        team_q = teams_str.split('?')
        print team_q
        team_lst=[]
        for i in team_q:
            team_lst.append([a.strip() for a in i.split(',')])
        print team_lst
        count=Team.objects.all().count()
        for t in team_lst:
            count+=1

            team = Team.objects.create(name='Team-'+str(count)+' ' + event.name, event=event)
            x=0
            for mem in t:
                if re.match(r'\d{7}', mem):
                    try:
                        p = Participant.objects.get(ems_code=mem)
                    except:
                        team.delete()
                        messages.warning(request, 'put the codes properly')
                        return redirect(request.META.get('HTTP_REFERER'))
                    team.members.add(p)
                    if x==0:
                        team.leader = p
                elif re.match(r'[h,f]\d{6}', mem):
                    try:
                        b = Bitsian.objects.filter(ems_code=mem)[0]
                    except:
                        team.delete()
                        messages.warning(request, 'put the codes properly')
                        return redirect(request.META.get('HTTP_REFERER'))
                    team.members_bitsian.add(b)
                    if x==0:
                        team.leader_bitsian = b
                else:
                    team.delete()
                    messages.warning(request, 'put the codes properly')
                    return redirect(request.META.get('HTTP_REFERER'))
                x+=1
            team.save()
            level.teams.add(team)
            s = Score(team=team, level=level)
            s.save()
        messages.success(request, 'teams added successfully.')
    return redirect(reverse('ems:team_home', kwargs={'e_id':e_id}))

@permission_for_event
@staff_member_required(login_url=login_url)
def team_details_home(request, e_id):
    event = Event.objects.get(id=e_id)
    teams = event.team_set.all()
    return render(request, 'ems/team_details_home.html', {'event':event, 'teams':teams})


@permission_for_event
@staff_member_required(login_url=login_url)
def team_details(request, e_id, team_id):

    event = Event.objects.get(id=e_id)
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        data = request.POST
        try:
            teams_lst = [a.strip() for a in data['ids'].split(',')]
        except:
            messages.warning(request, 'put the codes properly')
            return redirect(request.META.get('HTTP_REFERER'))
        l1=[]
        l2=[]
        for t in team_lst:
            if re.match(r'\d{7}', t):
                try:
                    p = Participant.objects.get(ems_code=t)
                    l1.append(p)
                except:
                    messages.warning(request, 'put the codes properly')
                    return redirect(request.META.get('HTTP_REFERER'))
            elif re.match(r'[h,f]\d{6}', mem):
                try:
                    b = Bitsian.objects.get(ems_code=mem)
                    l2.append(b)
                except:
                    messages.warning(request, 'put the codes properly')
                    return redirect(request.META.get('HTTP_REFERER'))
            else:
                messages.warning(request, 'put the codes properly')
                return redirect(request.META.get('HTTP_REFERER'))
        if data['submit'] == 'add':
            for i in l1:
                team.members.add(i)
            for i in l2:
                team.members_bitsian.add(i)
            team.save()
            messages.success(request, 'members added successfully.')
            return redirect(reverse('ems:team_deatils', kwargs={'e_id':event.id, 'team_id':team.id}))
        if data['submit'] == 'delete':
            try:
                team_lst = dict(data)['delete']
            except:
                messages.warning(request, 'Select atleast one member')
                return redirect(request.META.get('HTTP_REFERER'))
            l1=[]
            l2=[]
            for t in team_lst:
                if re.match(r'\d{7}', t):
                    try:
                        p = Participant.objects.get(ems_code=t)
                        l1.append(p)
                    except:
                        messages.warning(request, 'put the codes properly')
                        return redirect(request.META.get('HTTP_REFERER'))
                elif re.match(r'[h,f]\d{6}', t):
                    try:
                        b = Bitsian.objects.get(ems_code=t)
                        l2.append(b)
                    except:
                        messages.warning(request, 'put the codes properly')
                        return redirect(request.META.get('HTTP_REFERER'))
                else:
                    messages.warning(request, 'put the codes properly')
                    return redirect(request.META.get('HTTP_REFERER'))
            for i in l1:
                team.members.remove(i)
            for i in l2:
                team.members_bitsian.remove(i)
            team.save()

        try:
            leader_id = data['leader']
            if re.match(r'\d{7}', leader_id):
                p = Participant.objects.get(ems_code=leader_id)
                team.leader = p
            elif re.match(r'[h,f]\d{6}', leader_id):
                b = Bitsian.objects.get(ems_code=leader_id)
                team.leader_bitsian = b
            team.save()
        except:
            pass
    scores = [{'total':score.get_total_score(), 'level':score.level}for score in team.score_set.all()]
    return render(request, 'ems/team_details.html', {'event':event, 'team':team, 'scores':scores})

@permission_for_event
@staff_member_required(login_url=login_url)
def scores_level(request, e_id, level):
    event = Event.objects.get(id=e_id)
    level = get_object_or_404(Level,position=level, event=event)
    teams = level.teams.all()
    params = level.parameter_set.all()
    if request.POST == 'POST':
        data = request.POST
        for team in teams:
            score = team.score_set.get(level=level)
            score_dict = score.get_score()
            for param in params:
                key = str(team.id) + ' ' + str(parma.id)
                try:
                    value = data['key']
                    if not value:
                        raise Exception
                    score_dict[param.id] = value
                except:
                    pass
            score.score = str(score_dict)
            score.save()

    tables = [{'name':team.name, 'score':team.score_set.get(level=level).get_score()} for team in teams]
    return render(request, 'ems/score.html', {'tables':tables, 'parameters':params, 'event':event, 'level':level})


def user_logout(request):
    logout(request)
    return redirect('ems:index')

@permission_for_event
@staff_member_required(login_url=login_url)
def select_winner(request, e_id):
    event = Event.objects.get(id=e_id)
    levels = event.level_set.all()
    position = max([l.position for l in levels])
    final_level = Level.objects.get(event=event, position=position)
    finalists = final_level.teams.all()
    if request.method == 'POST':
        data = request.POST
        team_id = data['team_id']
        team = get_object_or_404(Team, id=team_id)
        if all([not t.is_winner for team in finalists]) and team in finalists:
            team.is_winner = True
    return render(request, 'ems/select_winner.html', {'event':event, 'teams':finalists})

@staff_member_required
def add_judge(request):
    if not(request.user.username == 'controls' or request.user.is_superuser):
        return redirect('ems:index')
    if request.method == 'POST':
        data = request.POST
        if data['submit'] == 'delete':
            try:
                judge_ids = data['judge_id']
            except:
                messages.warning(request, 'Please Select atleast 1')
                return redirect(request.META.get('HTTP_REFERER'))
            judges = Judge.objects.filter(id__in=judge_ids)
            for j in judges:
                j.user.delete()
                j.delete()
        else:
            name = data['name']
            event = Event.objects.get(id=data['event_id'])
            judge = Judge.objects.create(name=name, event=event)
            password = ''.join(choice(chars) for _ in xrange(8))
            user = User.objects.create_user(username='judge'+str(judge.id), password=password)
            judge.user = user
            judge.password = password
            judge.save()
    events = Event.objects.all()
    judges = Judge.objects.all()
    return render(request, 'ems/add_judge.html', {'events':events, 'judges':judges})

@staff_member_required
def add_cd(request):
    if request.method == 'POST':
        data = request.POST

        if data['submit'] == 'delete':
            try:
                cd_id = dict(data)['cd_id']
            except:
                messages.warning(request, 'Please Select atleast 1')
                return redirect(request.META.get('HTTP_REFERER'))
            cds = ClubDepartment.objects.filter(id__in=cd_id)
            for cd in cds:
                cd.user.delete()
                cd.events.clear()
                cd.delete()
        else:
            try:            
                name = data['name']
                event_ids = dict(data)['event_ids']
                co_ordinator = data['co_ordinator']
                phone = data['phone']
                email = data['email']
                if not re.match(r"\d{10}", phone) or not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                    raise Exception
            except:
                messages.warning(request, 'Fill the details properly.')
                return redirect(request.META.get('HTTP_REFERER'))
            events = Event.objects.filter(id__in=event_ids)
            cd = ClubDepartment.objects.create(name=name, co_ordinator=co_ordinator, phone=phone, email_id=email)
            password = ''.join(choice(chars) for _ in xrange(8))
            user = User.objects.create_user(username=cd.name.split()[0]+str(cd.id), password=password)
            cd.user = user
            cd.password = password
            for event in events:
                cd.events.add(event)
            cd.save()
    events = Event.objects.all()
    cds = ClubDepartment.objects.all()
    return render(request, 'ems/add_cd.html', {'events':events, 'cds':cds})

@staff_member_required
def add_bitsian(request):
    from django.conf import settings
    import os
    import csv

    f=open(os.path.join(settings.BASE_DIR, 'media', 'hostel_list.csv'))
    data = csv.reader(f)
    for row in data:
        b=Bitsian.objects.create(long_id=row[0], name=row[1])
        x=1 if row[2]=='' else 0
        gender = row[x+2]
        email = row[x+5].strip()
        y = email.split('@')[0]
        ems_code = y[0] + y[3:5] + y[5:].rjust(4,'0')
        b.ems_code=ems_code
        b.gender = gender
        b.email = email
        b.save()
    return HttpResponse('Good')

@staff_member_required
def gen_emscode(request):
    for a in Participant.objects.filter(pcr_approved=True):
        a.ems_code = str(a.college.id).rjust(3,'0')+str(a.id).rjust(4,'0')
        a.save()
    return HttpResponse('Good')