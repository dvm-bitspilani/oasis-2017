import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.static import serve
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse_lazy

def home(request):
	user = request.user
	day1 = Day.objects.get(day_no=1).is_active
	day2 = Day.objects.get(day_no=2).is_active
	day3 = Day.objects.get(day_no=3).is_active

	context = {'day1':day1, 'day2':day2, 'day3':day3}
	if user.is_authenticated():
		context['player'] = Player.objects.get(user=user)
	return render(request, 'wordwars/index.html', context)

@login_required(login_url='/wordwars')
def play(request, day=None):
	user = request.user
	player = Player.objects.get(user=user)
	day1 = Question.objects.filter(day__day_no=1).count()
	day2 = Question.objects.filter(day__day_no=2).count()
	day3 = Question.objects.filter(day__day_no=3).count()
	context = {'day1':day1, 'day2':day2, 'day3':day3, 'player':player}

	if day==1 or day is None:
		if player.day1 == day1:
			messages.success(request, 'This day is already complete. Wait for the day to end or start attempting Day-2.')
			return redirect(reverse_lazy('wordwars:home'))
		question = Question.objects.get(day__day_no=1, question_no=player.day1+1)
		if request.method == 'POST':
			try:
				ans = request.POST['answer']
			except:
				messages.warning(request, 'Don\'t leave the field empty' )
				return redirect(request.META.get('HTTP_REFERER'))
			if ans == question.answer:
				player.day1 += 1
				player.score += question.points
				player.save()
				messages.warning(request, 'Correct!')
				question = Question.objects.get(day__day_no=1, question_no=player.day1+1)
			else:
				messages.warning(request, 'Wrong Answer!!!!!')
	if day==2:
		if player.day2 == day2:
			messages.success(request, 'This day is already complete. Wait for the day to end or start attempting Day-3.')
			return redirect(reverse_lazy('wordwars:home'))
		question = Question.objects.get(day__day_no=2, question_no=player.day2+1)
		if request.method == 'POST':
			try:
				ans = request.POST['answer']
			except:
				messages.warning(request, 'Don\'t leave the field empty' )
				return redirect(request.META.get('HTTP_REFERER'))
			if ans == question.answer:
				player.day2 += 1
				player.score += question.points
				player.save()
				messages.warning(request, 'Correct!')
				question = Question.objects.get(day__day_no=2, question_no=player.day2+1)
			else:
				messages.warning(request, 'Wrong Answer!!!!!')
	if day == 3:
		if player.day3 == day3:
			messages.success(request, 'Congratulations! You have successfully completed all the questions.')
			return redirect(reverse_lazy('wordwars:home'))
		question = Question.objects.get(day__day_no=3, question_no=player.day3+1)
		if request.method == 'POST':
			try:
				ans = request.POST['answer']
			except:
				messages.warning(request, 'Don\'t leave the field empty' )
				return redirect(request.META.get('HTTP_REFERER'))
			if ans == question.answer:
				player.day3 += 1
				player.score += question.points
				player.save()
				messages.warning(request, 'Correct!')
				question = Question.objects.get(day__day_no=3, question_no=player.day3+1)
			else:
				messages.warning(request, 'Wrong Answer!!!!!')
	context['question'] = 0
	return render(request, 'wordwars/question.html', context)

def register(request):
	if request.method == 'POST':
		data = request.POST
		try:
			email = data['email']
			username = data['username']
			password = data['password']
			phone = data['phone']
			if email in [p.email for p in Player.objects.all()] or User.objects.filter(username=username):
				messages.warning(request, 'Username and Email Id must be unique')
				return redirect(request.META.get('HTTP_REFERER'))
			if not re.match(r"\d{10}", phone) or not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
				messages.warning(request, 'Invalid Phone Number or Email')
				return redirect(request.META.get('HTTP_REFERER'))

		except:
			messages.warning(request, 'Fill all the details Properly.')
			return redirect(request.META.get('HTTP_REFERER'))

		user = User.objects.create_user(username=username, password=password)
		player = Player.objects.create(user=user, email=email, phone=int(phone))
		login(request, user)
		return redirect('wordwars:home')

	return render(request, 'wordwars/register.html')

def user_login(request):
	if request.method == 'POST':
		try:
			username = request.POST['username']
			password = request.POST['password']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		user = authenticate(username=username, password=password)
		if user is None:
			messages.warning(request, 'Invalid login credentials')
			return redirect(request.META.get('HTTP_REFERER'))
		login(request, user)
		if user.is_staff:
			return render(request, 'wordwars/add_question.html')
		return redirect(reverse_lazy('wordwars:home'))
	return render(request, 'wordwars/login.html')

def user_logout(request):
	logout(request)
	return render(request, 'wordwars/index.html')

def leaderboard(request):
	players = Player.objects.all().order_by('-score')
	return render(request, 'wordwars/leaderboard.html', {'players':players})

def rulespage(request):
	return render(request, 'wordwars/rulespage.html')

def instructions(request):
	instructions_ = '/home/dvm/oasis/oasis2017/static/wordwars/docs/Instructions.pdf'
	serve(request, os.path.basename(instructions_), os.path.dirname(instructions_))

def rules(request):
	rules_ = '/home/dvm/oasis/oasis2017/static/wordwars/docs/Rules.pdf'
	serve(request, os.path.basename(rules_), os.path.dirname(rules_))

def contact(request):
	return render(request, 'wordwars/contact.html')

@staff_member_required
def add_question(request):
	if request.method == 'POST':
		data = request.POST
		try:
			day = data['day']
			day = get_object_or_404(Day, day_no=day)
			answer = data['answer']
			points = data['points']
			image = request.FILES['image']
		except:
			messages.warning(request, 'Invalid Question')
			return redirect(request.META.get('HTTP_REFERER'))
		question_no = Question.objects.filter(day=day).count()+1
		question = Question.objects.create(day=day, answer=answer, question_no=question_no, points=points)
		question.image.save('question', image)
		messages.success(request, 'Question successfully added. Add Another')
	return render(request, 'wordwars/add_question.html')

@staff_member_required
def day_activate(request):
	if request.method == 'POST':
		try:
			days = request.POST['day']
		except:
			return redirect(request.META.get('HTTP_REFERER'))	
		days = Day.objects.filter(day_no=day).update(is_active=True)
		return redirect(reverse_lazy('wordwars:home'))
	day1 = Day.objects.get(day_no=1).is_active
	day2 = Day.objects.get(day_no=2).is_active
	day3 = Day.objects.get(day_no=3).is_active
	return render(request, 'wordwars/day_activate.html',{'day1':day1, 'day2':day2, 'day3':day3})
