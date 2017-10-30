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
from django.contrib.auth.decorators import login_required
chars = string.letters + string.digits

login_url = reverse_lazy('ems:login')


######### DECORATORS #########

def permission_for_cd(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        event = get_object_or_404(Event, pk=kwargs['e_id'])
        try:
            club_dept = ClubDepartment.objects.get(user=user)
            if not event in list(club_dept.events.all()):
                pass
        except:
            url = reverse_lazy('ems:events_select')
            return render(request, 'registrations/message.html',  {'error_heading':'Invalid access', 'message':'You do not have access to this page.', 'url':url})
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def permission_for_judge(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        level = get_object_or_404(Level, pk=kwargs['level_id'])
    # try:
        judge = Judge.objects.get(user=user, level=level)
        if judge.left_the_event:
            context = {
            'error_heading': "Invalid Access.",
            'message': "You left this event, Now you are not allowed to judge it anymore.",
            'url':'https://bits-oasis.org'
            }
            return render(request, 'registrations/message.html', context)
        return function(request, *args, **kwargs)
    # except:
        logout(request)
        return redirect('ems:index')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def permission_for_controls(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.username=='controls':
            return function(request, *args, **kwargs)
        else:
            logout(request)
            return redirect('ems:index')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

######### DECORATORS END #########


def index(request):
    if request.user.is_authenticated():
        if request.user.is_superuser or request.user.username=='controls':
            return redirect(reverse_lazy('ems:events_controls'))
        try:
            judge = request.user.judge
            return redirect(reverse('ems:update_scores', kwargs={'level_id':judge.level.id}))
        except:
            pass
        try:
            cd = ClubDepartment.objects.get(user=request.user)
            return redirect('ems:events_select')
        except:
            pass
        logout(request)
    return redirect(reverse_lazy('ems:login'))


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('ems:index')    
        else:
            messages.warning(request, 'Invalid credentials')
            return redirect(request.META.get('HTTP_REFERER'))
    return render(request, 'ems/login.html')




######### CLUB 'N' DEPARTMENTS #########


@login_required(login_url=login_url)
def events_select(request):                     ### done
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


@login_required(login_url=login_url)
@permission_for_cd
def add_delete_teams(request, e_id):                ### done
    event = get_object_or_404(Event, id=e_id)
    count = Team.objects.filter(event=event).count()
    try:
        level = Level.objects.get(position=1, event=event)
    except:
        messages.warning(request, 'First add atleast one level for this event')
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST':
        data = dict(request.POST)
        submit = ''
        try:
            submit = data['submit'][0]
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        if data['submit'][0] == 'delete_teams':
            try:
                team_ids = data['delete_team_id']
            except:
                messages.warning(request, 'Select atleast one team')
                return redirect(request.META.get('HTTP_REFERER'))
            Team.objects.filter(id__in=team_ids).delete()
            return redirect(reverse('ems:add_team', kwargs={'e_id':e_id}))
        try:
            teams_str = data['teams'][0]
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        team_q = teams_str.split('?')
        team_lst=[]
        for i in team_q:
            team_lst.append([a.strip() for a in i.split(',')])
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

@login_required(login_url=login_url)
@permission_for_cd
def team_details_home(request, e_id):                ### done
    event = Event.objects.get(id=e_id)
    teams = event.team_set.all()
    return render(request, 'ems/team_details_home.html', {'event':event, 'teams':teams})

@login_required(login_url=login_url)
@permission_for_cd
def team_details(request, e_id, team_id):           ### done

    event = Event.objects.get(id=e_id)
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        data = request.POST
        try:
            teams_lst = [a.strip() for a in data['teams'].split(',')]
        except:
            messages.warning(request, 'put the codes properly')
            return redirect(request.META.get('HTTP_REFERER'))
        l1=[]
        l2=[]
        for t in teams_lst:
            if re.match(r'\d{7}', t):
                try:
                    p = Participant.objects.get(ems_code=t)
                    l1.append(p)
                except:
                    messages.warning(request, 'unmacthed ems codes')
                    return redirect(request.META.get('HTTP_REFERER'))
            elif re.match(r'[h,f]\d{6}', t):
                try:
                    b = Bitsian.objects.filter(ems_code=t)[0]
                    l2.append(b)
                except:
                    messages.warning(request, 'unmacthed ems codes')
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
            return redirect(reverse('ems:team_home', kwargs={'e_id':event.id})+team_id+'/')
        # if data['submit'] == 'delete':
        #     try:
        #         team_lst = dict(data)['delete']
        #     except:
        #         messages.warning(request, 'Select atleast one member')
        #         return redirect(request.META.get('HTTP_REFERER'))
        #     l1=[]
        #     l2=[]
        #     for t in team_lst:
        #         if re.match(r'\d{7}', t):
        #             try:
        #                 p = Participant.objects.get(ems_code=t)
        #                 l1.append(p)
        #             except:
        #                 messages.warning(request, 'put the codes properly')
        #                 return redirect(request.META.get('HTTP_REFERER'))
        #         elif re.match(r'[h,f]\d{6}', t):
        #             try:
        #                 b = Bitsian.objects.get(ems_code=t)
        #                 l2.append(b)
        #             except:
        #                 messages.warning(request, 'put the codes properly')
        #                 return redirect(request.META.get('HTTP_REFERER'))
        #         else:
        #             messages.warning(request, 'put the codes properly')
        #             return redirect(request.META.get('HTTP_REFERER'))
        #     for i in l1:
        #         team.members.remove(i)
        #     for i in l2:
        #         team.members_bitsian.remove(i)
        #     team.save()

        # try:
        #     leader_id = data['leader']
        #     if re.match(r'\d{7}', leader_id):
        #         p = Participant.objects.get(ems_code=leader_id)
        #         team.leader = p
        #     elif re.match(r'[h,f]\d{6}', leader_id):
        #         b = Bitsian.objects.get(ems_code=leader_id)
        #         team.leader_bitsian = b
        #     team.save()
        # except:
        #     pass
    team = get_object_or_404(Team, id=team_id)
    scores = [{'total':score.get_total_score(), 'level':score.level}for score in team.scores.all()]
    return render(request, 'ems/team_details.html', {'event':event, 'team':team, 'scores':scores, 'members':team.members.all(), 'bitsians':team.members_bitsian.all()})


######### END CD #########


######### JUDGEs #########


@permission_for_judge
@login_required(login_url=login_url)
def update_scores(request, level_id):               ### done
    judge = request.user.judge
    j_id = judge.id
    level = Level.objects.get(id=level_id)
    event = level.event
    teams = Team.objects.filter(event=event)
    params = level.parameter_set.all()
    if request.method == 'POST':
        data = request.POST
        if data['submit'] == 'leave':
            judge.left_the_event = True
            judge.save()
            return redirect(reverse('ems:update_scores', kwargs={'level_id':level_id}))
        for team in teams:
            try:
                score = team.scores.get(level=level)
            except:
                continue
            score.save()
            if judge.frozen:
                continue
            try:
                comment = data['comment-'+str(team.id)]
                comment_dict = score.get_comments()
                comment_dict[j_id] = comment
                score.comments = str(comment_dict)

            except:
                pass
            score_dict_total = score.get_score()
            score_dict = score.get_score_j(j_id)
            for param in params:
                key = str(team.id) + '-' + str(param.id)
                try:
                    value = int(data[key])
                    if (not value or value>param.max_val) and not value==0:
                        raise Exception
                    score_dict[param.id] = value
                except:
                    pass
            score_dict_total[j_id] = score_dict
            score.score_card = str(score_dict_total)

            score.save()
        messages.success(request, 'Score updated successfully')
        if data['submit'] == 'lock':
            judge.frozen=True
            judge.save()
    tables = []
    for team in teams:
        try:
            score = team.scores.get(level=level)
            tables.append({'team':team,'score':score, 'score_dict':score.get_score_j(j_id), 'comment':score.get_comment_j(j_id)})
        except:
            continue
    if not tables:
        context = {'error_heading':'No Teams in this level', 'message':'No teams is promoted to this level.', 'url':'#'}
        return render(request, 'registrations/message.html')
    return render(request, 'ems/update_scores.html', {'teams':tables, 'parameters':params, 'event':event, 'level':level, 'judge':judge})


# @login_required(login_url=login_url)
# def show_scores(request, e_id, level_id):
#     try:
#         judge = request.user.judge
#     except:
#         logout(request)
#         return redirect('ems:index')
#     j_id = judge.id
#     event = Event.objects.get(id=e_id)
#     level = get_object_or_404(Level,id=level_id, event=event)
#     params = level.parameter_set.all()
#     teams = Team.objects.filter(event=event)
#     if request.method == 'POST':
#         try:
#             team_ids = dict(request.POST)['team_id']
#             teamss = Team.objects.filter(id__in=team_ids)
#             Score.objects.filter(team__in=teamss,level=level).update(is_frozen=True)
#         except:
#             messages.success(request, 'No team chosen')
#             pass
    
#     tables = []
#     for team in teams:
#         try:
#             tables.append({'team':team, 'score':team.scores.get(level=level), 'score_dict':team.scores.get(level=level).get_score_j(j_id)})
#         except:
#             continue

#     return render(request, 'ems/show_scores.html', {'teams':tables, 'parameters':params, 'event':event, 'level':level})





######### END JUDGE #########

######### CONTROLS #########


@permission_for_controls
@login_required(login_url=login_url)
def event_home(request, e_id):                  ### done
    event = get_object_or_404(Event, id=e_id)
    if request.method == 'POST':
        data = request.POST
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
                score, created = Score.objects.get_or_create(team=team, level=next_level)
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
                score, created = Score.objects.get_or_create(team=team, level=prev_level)
        # elif "add-finalists" == data['submit']:
        #     teamids = request.POST.getlist('registered')
        #     Team.objects.filter(id__in=teamids).update(is_finalist=True)
        # elif "remove-finalists" == data['submit']:
        #     teamids = request.POST.getlist('finalists')
        #     Team.objects.filter(id__in=teamids).update(is_finalist=False)
        elif "add-winners" == data['submit']:
            try:
                next_level = Level.objects.get(event=event, position = position + 1)
                messages.warning(request, 'Sorry first promote them to highest level.')
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                pass
            if all([t.level==position for t in team_list]):
                team_list.update(is_winner=True)
            else:
                messages.warning(request, 'Sorry first promote them to highest level.')
                return redirect(request.META.get('HTTP_REFERER'))
        elif "remove-winners" == data['submit']:
            team_list.update(is_winner=False)
    levels = Level.objects.filter(event=event)
    positions = range(levels.count(),0,-1)
    tables = [{'level':p, 'teams':sorted([{'team':team, 'score':Score.objects.get(team=team, level=Level.objects.get(event=event, position=p)).get_total_score()} for team in Team.objects.filter(event=event, level=p)], key=lambda x:-x['score'])} for p in positions]
    winners = event.team_set.filter(is_winner=True)
    context = {'event':event,'levels':levels, 'tables':tables}
    if winners:
        w_position = winners[0].level
        winners_list = [{'team':team, 'score':Score.objects.get(team=team, level=Level.objects.get(event=event, position=w_position)).get_total_score()} for team in winners]
        context['winners'] = winners_list
        context['w_position'] = w_position
    return render(request, 'ems/event_home.html', context)


@permission_for_controls
@login_required(login_url=login_url)
def event_levels(request, e_id):                    ### done
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


@permission_for_controls
@login_required(login_url=login_url)
def event_levels_add(request, e_id):                 ### done
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
            maxes = list(map(lambda x: int(x.strip()), data['values'].split('?')))
            if not len(names) == len(maxes):
                raise Exception
        except:
            messages.warning(request, 'Please Fill the details of the level properly')
            return redirect(request.META.get('HTTP_REFERER'))
        level = Level.objects.create(name=name, position=position+1, event=event)
        for i, n in enumerate(names):
            p=Parameter.objects.create(name=n, max_val=int(maxes[i]), level=level)
        return redirect(reverse_lazy('ems:event_levels', kwargs={'e_id':event.id}))
    context = {'event':event, 'levels':levels, 'position':position}
    return render(request, 'ems/event_levels_add.html', context)


@permission_for_controls
@login_required(login_url=login_url)
def show_level(request, level_id):                  ### done
    level = get_object_or_404(Level, id=level_id)
    event = level.event
    params = level.parameter_set.all()
    return_url = request.META.get('HTTP_REFERER')
    print return_url
    return render(request, 'ems/show_level.html', {'event':event, 'level':level, 'params':params, 'return':return_url})




@permission_for_controls
@staff_member_required
def events_controls(request):                       ### done
    events = Event.objects.all()
    return render(request, 'ems/events_controls.html', {'events':events})


@permission_for_controls
@staff_member_required
def show_score_controls(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    levels = event.level_set.all()
    if not levels:
        messages.warning(request, 'No levels in this event.')
        return redirect(request.META.get('HTTP_REFERER'))
    tables = []
    for level in levels:
        judges = Judge.objects.filter(level=level)
        teams = Team.objects.filter(event=event)
        params = level.parameter_set.all()
        headings = ['Name', 'Leader'] + [judge.name for judge in judges] + ['Total',]
        table = {'title':level.name+' ' + str(level.position), 'headings':headings}
        rows = []
        for team in teams:
            if team.leader:
                leader = team.leader
            else:
                leader = team.leader_bitsian
            try:
                score = team.scores.get(level=level)
            except:
                continue
            rows.append({'data':[team.name, leader]+[score.get_total_j(judge.id) for judge in judges] + [score.get_total_score()]})
        table['rows'] = rows
        table['judges'] = judges
        tables.append(table)
    return render(request, 'ems/show_score_controls.html', {'tables':tables, 'event':event})


@permission_for_controls
@staff_member_required
def show_score_controls_judge(request, e_id, judge_id):
    event = Event.objects.get(id=e_id)
    judge = Judge.objects.get(id=judge_id)
    level = judge.level
    params = level.parameter_set.all()
    teams = event.team_set.all()
    headings = ['Name', 'Leader'] + [p for p in params] + ['Total', 'Comments']
    rows = []
    for team in teams:
        try:
            score = Score.objects.get(team=team, level=level)
        except:
            continue
        if team.leader:
            leader = team.leader
        else:
            leader = team.leader_bitsian
        rows.append([team.name, leader] + [score.get_score_j_p(judge.id, p.id) for p in params] + [score.get_total_j(judge.id), score.get_comment_j(judge.id)])
    return render(request, 'ems/show_score_controls_judge.html', {'event':event, 'judge':judge, 'level':level, 'rows':rows, 'headings':headings})


@permission_for_controls
@staff_member_required
def add_judge(request, e_id):                ### done
    event = get_object_or_404(Event, id=e_id)
    levels = event.level_set.all()
    if not levels:
        messages.warning(request, 'No levels in this event.')
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST':
        data = request.POST
        if data['submit'] == 'delete':
            try:
                judge_ids = dict(data)['judge_id']
            except:
                messages.warning(request, 'Please Select atleast one entry.')
                return redirect(request.META.get('HTTP_REFERER'))
            judges = Judge.objects.filter(id__in=judge_ids)
            for j in judges:
                l = j.level
                for score in Score.objects.filter(level=l):
                    score_dict = score.get_score()
                    try:
                        del(score_dict[j_id])
                        score.score_card = str(score_dict)
                        score.save()
                    except:
                        pass
                j.user.delete()
                j.delete()
        
        elif data['submit'] == 'add':
            name = data['name']
            level = Level.objects.get(id=data['level_id'])
            judge = Judge.objects.create(name=name, level=level)
            chars = string.letters + string.digits
            a = list(chars)
            a.pop(11)
            a.pop(33)
            chars = ''.join(a)
            password = ''.join(choice(chars) for _ in xrange(8))
            user = User.objects.create_user(username='judge'+str(judge.id), password=password)
            judge.user = user
            judge.save()
            for team in Team.objects.filter(event=event):
                for s in team.scores.all():
                    s.save()
            return render(request, 'ems/judge_details.html', {'judge':judge, 'password':password, 'event':event, 'level':level, 'url':request.META.get('HTTP_REFERER')})
        elif data['submit'] == 'freeze':
            try:
                judge_ids = dict(data)['judge_id']
                print judge_ids
            except:
                messages.warning(request, 'Please Select atleast one entry.')
                return redirect(request.META.get('HTTP_REFERER'))
            judges = Judge.objects.filter(id__in=judge_ids)
            judges.update(frozen=True)
            print 'done'
        elif data['submit'] == 'discard':
            try:
                judge_ids = dict(data)['judge_id']
            except:
                messages.warning(request, 'Please Select atleast one entry.')
                return redirect(request.META.get('HTTP_REFERER'))
            judges = Judge.objects.filter(id__in=judge_ids)
            judges.update(left_the_event=True)

    judges = Judge.objects.filter(level__event=event)
    return render(request, 'ems/add_judge.html', {'event':event,'levels':levels, 'judges':judges})


@permission_for_controls
@staff_member_required
def add_cd(request):                #### done
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
            chars = string.letters + string.digits
            a = list(chars)
            a.pop(11)
            a.pop(33)
            chars = ''.join(a)
            password = ''.join(choice(chars) for _ in xrange(8))
            user = User.objects.create_user(username=cd.name.split()[0]+str(cd.id), password=password)
            cd.user = user
            for event in events:
                cd.events.add(event)
            cd.save()
            return render(request, 'ems/cd_details.html', {'cd':cd, 'event':event, 'password':password, 'url':request.META.get('HTTP_REFERER')})
    events = Event.objects.all()
    cds = ClubDepartment.objects.all()
    return render(request, 'ems/add_cd.html', {'events':events, 'cds':cds})


############ END CONTROLS #########


@staff_member_required
def add_bitsian(request):
    if not request.user.is_superuser:
        logout(request)
        return redirect('ems:index')
    import os
    import csv
    import re
    from django.conf import settings

    f=open(os.path.join(settings.BASE_DIR, 'media', 'hostel_list.csv'))
    data = csv.reader(f)
    response = 'Good  '
    for row in data:
        try:
            b = Bitsian.objects.get(long_id=row[0], name=row[1])
            continue
        except:
            b = Bitsian(long_id=row[0], name=row[1])
        ld = row[0]
        email = 'f'
        if 'H' in row[0]:
            email = 'h'
        ems_code = email
        ems_code += ld[2:4] + ld[-4:]
        match1 = re.search(r'(\d{4})\w{4}0(\d{3})', ld)
        match2 = re.search(r'(\d{4})\w{4}1(\d{3})', ld)
        if match1:
            email += match1.group(1) + match1.group(2) + '@pilani.bits-pilani.ac.in'
        elif match2:
            email += match2.group(1) + '1' + match2.group(2) + '@pilani.bits-pilani.ac.in'
        print email
        b.ems_code=ems_code
        # b.gender = gender
        b.barcode = ''.join(choice(chars) for _ in xrange(8))
        b.email = email
        b.save()
        break
    return HttpResponse(response)

@staff_member_required
def gen_emscode(request):
    for a in Participant.objects.filter(pcr_approved=True):
        a.ems_code = str(a.college.id).rjust(3,'0')+str(a.id).rjust(4,'0')
        a.save()
    return HttpResponse('Good')


def user_logout(request):
    logout(request)
    return redirect('ems:index')