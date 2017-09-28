from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404
from registrations.models import *
from events.models import *
from .models import *
import re


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
        position = int(data['position'])
        try:
            level = Level.objects.get(event=event, position=position)
        except:
            url = request.build_absolute_uri(reverse_lazy('ems:event_home', kwargs={'e_id':event.id}))
            return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'This level does not exist. Please add it from Manage Levels tab.', 'url':url})
        try:
            lst = data.getlist('team_list')
            team_list = Team.objects.filter(id__in=lst)
        except:
            url = request.build_absolute_uri(request.META.get('HTTP_REFERER'))
            return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'Please Select atleast 1 Team', 'url':url})

        if data['submit'] == 'Promote':
            try:
                next_level = Level.objects.get(event=event, position = position + 1)
            except:
                url = request.build_absolute_uri(reverse_lazy('ems:event_home', kwargs={'e_id':event.id}))
                return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'The next level does not exist. Please add it from Manage Levels tab.', 'url':url})
            for team in team_list:
                if team not in level.teams.all():
                    url = request.build_absolute_uri(reverse_lazy('ems:event_home', kwargs={'e_id':event.id}))
                    return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'A team was not in the current level. Please add it.', 'url':url})   
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
                url = request.build_absolute_uri(reverse_lazy('ems:event_home', kwargs={'e_id':event.id}))
                return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'The previous level does not exist. Please add it from Manage Levels tab.', 'url':url})
            for team in team_list:
                level.teams.remove(team)
                prev_level.teams.add(team)
                team.level = position-1
                team.save()
                try:
                    score = Score.objects.get(team=team, level=prev_level)
                except:
                    score = Score.objects.create(team=team, level=prev_level)

    levels = Level.objects.filter(event=event)
    positions = range(1,levels.count()+1)
    tables = [{'level':p, 'teams':sorted([{'team':team, 'score':Score.objects.get(team=team, level=level).get_total_score()} for team in Team.objects.filter(event=event, level=p)], key=lambda x:-x['score'])} for p in positions].reverse()
    context = {'event':event,'levels':levels, 'tables':tables}
    return render(request, 'ems/event_home.html', context)


# @permission_for_event
# @staff_member_required(login_url=login_url)
# def add_judge(request, e_id):
#     event = get_object_or_404(Event, id=e_id)
#     clubdepartment = ClubDepartment.objects.get(user=request.user)

#     if request.method == 'POST':
#         data = request.POST
#         username = 'judge' + event.name.split()[0] + random.ranint(1,1000)
#         try:
#             password = data['password']
#             name = data['name']
#             if password=='' or name=='':
#                 raise Exception
#         except:
#             url = request.build_absolute_uri(reverse_lazy('ems:add_judge', kwargs={'e_id':e_id}))
#             return render(request, 'ems/message.html', {'error_heading':'User exists', 'message':'Don\'t leave the name and password field empty', 'url':url})
#         judge = Judge.objects.create(name=name, event=event, user=user)
#         return redirect(reverse_lazy('ems:event_home', {'e_id':e_id}))
#     return render(request, 'ems/add_judge.html', {'event':event})


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
        elif data['submit'] == 'delete-judge':
            try:
                j_id = data['j_id']
                judge = get_object_or_404(Judge, id=j_id)
            except:
                return redirect(request.META.get('HTTP_REFERER'))
            judge.delete()
    levels = Level.objects.filter(event=event)
    judges = Judge.objects.filter(event=event)
    context = {'event':event, 'levels':levels, 'judges':judges}
    return render(request, 'ems/event_levels.html', context)


@permission_for_event
@staff_member_required(login_url=login_url)
def event_levels_add(request, e_id):
    event = Event.objects.get(id=e_id)
    levels = Level.objects.get(event=event)
    position = Level.objects.filter(event=event).count()
    if request.method == 'POST':
        data = request.POST
        try:
            name = data['name']
            if name == '':
                raise Exception
            names = dict(data)['parameter_names']
            maxes = dict(data)['parameter_maxes']
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        level = Level.objects.create(name=name, position=position+1, event=event)
        for i, n in enumerate(names):
            p=Parameter.objects.create(name=n, max_value=maxes[i], level=level)
        return redirect(reverse_lazy('ems:event_levels', kwargs={'e_id':event.id}))
    context = {'event':event, 'levels':levels, 'position':position}
    return render(request, 'ems/event_levels_add.html', context)


@permission_for_event
@staff_member_required(login_url=login_url)
def add_team(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    if request.method == 'POST':
        data = dict(request.POST)
        try:
            parts_ids = data['parts']
            leader_id = data['leader'][0]
            parts = Participant.objects.filter(id__in=parts_ids)
            leader = Participant.objects.get(id=leader_id)
            name = data['name'][0]
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        team = Team(name=name, leader=leader, event=event)
        team.save()
        for part in parts:
            team.members.add(part)
        team.save()
        level = Level.objects.get(position=1, event=event)
        level.teams.add(team)
        Score.objects.create(team=team, level=level)
        submit = data['submit'][0]

        if submit == 'add':
            return redirect(reverse_lazy('ems:event_home'))
    parts = Participant.objects.filter(controlz_paid=True)
    bitsians = Bitsian.objects.all()
    return render(request, 'ems/add_team.html', {'event':event, 'participants':parts, 'bitsians':bitsians})


@permission_for_event
@staff_member_required(login_url=login_url)
def add_bitsian_team(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    try:
        level = Level.objects.get(event=event, position=1)
    except:
        return redirec(reverse_lazy('ems:event_home', kwargs={'e_id':e_id}))
    if request.method == 'POST':
        data = dict(request.POST)
        try:
            name = data['name']
            bits_ids = data['bits_id']
            names = data['names']
            if not len(names) == len(bits_ids):
                raise Exception
            leader_no = data['leader']
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        bitsians = []
        for i,bits_id in enumerate(bits_ids):
            b = Bitsian.objects.create(name=names[i], long_id=bits_id)
            bitsians.append(b)
            if leader_no == i:
                leader = b
        team = Team(name=name, event=event, leader=leader, is_bitsian=True)
        team.save()
        for b in bitsian:
            team.members_bitsian.add(b)
        team.save()
        level.teams.add(team)
        if submit == 'add':
            return redirect(reverse_lazy('ems:event_home'))
    return render(request, 'ems/add_bitsian.html', {'event':event})



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
    scores = [{'total':score.get_total_score(), 'level':score.level}for score in team.score_set.all()]
    return render(request, 'ems/team_details.html', {'event':event, 'team':team, 'scores':scores})


def user_logout(request):
    logout(request)
    return redirect('ems:index')


