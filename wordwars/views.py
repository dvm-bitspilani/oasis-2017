from django.shortcuts import render, redirect
from models import *
import os
from django.views.static import serve
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse

def home(request):

	return render(request, 'wordwars/index.html')

def play(request, day=None):
	pass

def register(request):
	try:
		data = request.POST
		email = data['email']
		username = data['username']
		password = data['password']
	except:
		messages.warning(request, 'Fill all the details')
		return home(request)

	if email in [p.email for p in Player.objects.all()] or User.objects.filter(username=username):
		messages.warning(request, 'Username and Email Id must be unique')
		return home(request)		

def user_login(request):
	pass

def user_logout(request):
	pass

def leaderboard(request):
	pass

def instructions(request):
	pass

def rules(request):
	pass

def rulespage(request):
	pass

def contact(request):
	pass