from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from . import views
from .models import *
from django.contrib.auth import logout

class WordWarsMiddleware(object):

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def process_view(self, request, view_func, view_args, view_kwargs):

		if 'wordwars' in request.path:
			if request.user.is_authenticated():

				if request.user.is_superuser:
					return redirect('/admin')

				try:
					day = view_kwargs['day']
				except:
					return None
				if day == None:
					return None
				day = get_object_or_404(Day, day_no=day)
				if not day.is_active:
					return redirect('wordwars:home')
		else:
			if request.user.is_authenticated():
				
				try:
					player = request.user.player
					logout(request)
					return None
				except:
					return None