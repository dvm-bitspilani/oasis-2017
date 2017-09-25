from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404
from registrations.models import *
from events.models import *
from .models import *

def index(request):
    if request.user.is_authenticated() and request.user.is_staff:
        return redirect(reverse('ems:events_select'))
    else:
        return redirect(reverse('ems:login'))


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                
                return HttpResponseRedirect(reverse('registrations:index'))
            else:
                url = request.build_absolute_uri(reverse('ems:index'))
                context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional Contacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .', 'url':url}
                return render(request, 'ems/message.html', context)
        else:
            url = request.build_absolute_uri(reverse('ems:index'))
            context = {'error_heading' : "Invalid Login Credentials", 'message' :  'Invalid Login Credentials. Please try again', 'url':url}
            return render(request, 'ems/message.html', context)

    else:
        return render(request, 'ems/login.html')



@staff_member_required
def events_select(request):
    if request.user.is_superuser:
        event_list = Event.objects.all()
    else:
        try:
            clubdept =  ClubDepartment.objects.get(user=request.user)
            event_list = clubdept.events.order_by('name')
        except:
            logout(request)
            return redirect(reverse('ems:index'))
    
    return render(request, 'ems/event_list.html', {'event_list':event_list})

@staff_member_required
def event_home(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    clubdepartment = ClubDepartment.objects.get(user=request.user)
    if request.user.is_superuser:
        continue
    elif not event in clubdepartment.events:
        url = request.build_absolute_uri(reverse('ems:events-select'))
        return render(request, 'ems/message.html', {'error_heading':'Invalid access', 'message':'You do not have access to this page.', 'url':url})
    if request.method == 'POST':
        data = request.POST
        position = int(data['position'])
        try:
            level = Level.objects.get(event=event, position=position)
        except:
            url = request.build_absolute_uri(reverse('ems:event_home', kwargs={'e_id':event.id}))
            return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'This level does not exist. Please add it from Manage Levels tab.', 'url':url})
        team_list = Team.objects.filter(id__in=data.getlist('team_list'))
        if data['submit'] == 'Promote':
            try:
                next_level = Level.objects.get(event=event, position = position + 1)
            except:
                url = request.build_absolute_uri(reverse('ems:event_home', kwargs={'e_id':event.id}))
                return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'The next level does not exist. Please add it from Manage Levels tab.', 'url':url})
            for team in team_list:
                if team not in level.teams.all():
                    url = request.build_absolute_uri(reverse('ems:event_home', kwargs={'e_id':event.id}))
                    return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'A team was not in the current level. Please add it.', 'url':url})   
                next_level.teams.add(team)
        
        elif data['submit'] == 'Demote':
            try:
                prev_level = Level.objects.get(event=event, position = position - 1)
            except:
                url = request.build_absolute_uri(reverse('ems:event_home', kwargs={'e_id':event.id}))
                return render(request, 'ems/message.html', {'error_heading':'Error!', 'message':'The previous level does not exist. Please add it from Manage Levels tab.', 'url':url})
            for team in team_list:
                level.teams.remove(team)

    levels = Level.objects.filter(event=event)
    context = {'event':event,'levels':levels}
    return render(request, 'ems/event_home.html', context)

@staff_member_required
def add_judge(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    clubdepartment = ClubDepartment.objects.get(user=request.user)
    if request.user.is_superuser:
        continue
    elif not event in clubdepartment.events:
        url = request.build_absolute_uri(reverse('ems:index'))
        return render(request, 'ems/message.html', {'error_heading':'Invalid access', 'message':'You do not have access to this page.', 'url':url})
    if request.method == 'POST':
        data = request.POST
        username = data['username']
        password = data['password']
        name = data['name']
        try:
            user = User.objects.create_user(username=username, password=password)
        except:
            url = request.build_absolute_uri(reverse('ems:add_judge', kwargs={'e_id':e_id}))
            return render(request, 'ems/message.html', {'error_heading':'User exists', 'message':'Please change the username.', 'url':url})
        judge = Judge.objects.create(name=name, event=event, user=user)
        return redirect(reverse('ems:event_home', {'e_id':e_id}))
    return render(request, 'ems/add_judge.html', {'event':event})

@staff_member_required
def create_label(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    clubdepartment = ClubDepartment.objects.get(user=request.user)
    if request.user.is_superuser:
        continue
    elif not event in clubdepartment.events:
        url = request.build_absolute_uri(reverse('ems:index'))
        return render(request, 'ems/message.html', {'error_heading':'Invalid access', 'message':'You do not have access to this page.', 'url':url})
    if request.method == 'POST':
        data = request.POST
        label = Label.objects.get_or_create(event=event)
        try:
            names_list = data.getlist('names')
            max_list = data.getlist('max_list')
        except:
            request.META.get('HTTP_REFERRER')
        if not len(names_list) == len(max_list):
            url = request.build_absolute_uri(reverse('ems:create_label'))
            return render(request, 'ems/message.html', {'error_heading':'Invalid data', 'message':'Please enter data in a valid form.', 'url':url}) 
        count = 0
        data_list = []
        while(count<len(names_list)):
            data_list.append({'name':names_list[count], 'max_val':max_list[count]})
            count += 1
        
        for item in data_list:
            for name, val in item.iteritems():
                Parameter.objects.create(label=label, name=name, max_val=val)

        label.save()
    
    label_list = Label.objects.all()
    return render(request, 'ems/create_label.html', {'label_list':label_list})

@staff_member_required
def event_levels(request, e_id):
    event = get_object_or_404(Event, id=e_id)
    clubdepartment = ClubDepartment.objects.get(user=request.user)
    if request.user.is_superuser:
        continue
    elif not event in clubdepartment.events:
        url = request.build_absolute_uri(reverse('ems:events-select'))
        return render(request, 'ems/message.html', {'error_heading':'Invalid access', 'message':'You do not have access to this page.', 'url':url})
    if request.method == 'POST':
        data = request.POST
        if data['submit'] == 'delete-level':
            l_id = data['l_id']
            level = get_object_or_404(Level, id=l_id)
            level.teams.clear()
            level.delete()
        elif data['submit'] == 'delete-judge':
            j_id = data['j_id']
            judge = get_object_or_404(Judge, id=j_id)
            judge.level_set.clear()
    levels = Level.objects.filter(event=event)
    context = {'event':event, 'levels':levels}
    return render(request, 'ems/event_levels.html', context)

@staff_member_required
def event_levels_add(request, e_id):
    event = Event.objects.get(id=e_id)
    levels = Level.objects.get(event=event)
    if request.method == 'POST':
        data = request.POST
        name = data['name']
        position = int(data['position'])
        level = Level.objects.create(name=name, position=position, event=event)
        try:
            label_list = Label.objects.filter(id__in=data.getlist('labels'))
            for label in label_list:
                label.level = level
                label.save()
        except:
            pass
        try:
            judges_list = Judge.objects.filter(id__in=data.getlist('judge_list'))
            for judge in judges_list:
                level.judges.add(judge)
        except:
            pass
        return redirect(reverse('ems:event_levels', kwargs={'e_id':event.id}))
    position = (Level.objects.filter(event=event).count - 1)
    context = {'event':event, 'levels':levels, 'position':position}
    return render(request, 'ems/event_levels_add.html', context)

