from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from . import views
from .models import *
from django.contrib.auth import logout

class WordWarsMiddleware(object):

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def process_view(self, request, view_func, view_args, view_kwargs):

		if 'admin' in request.path and request.user.is_superuser:
			return None

		if 'wordwars' in request.path:
			if request.user.is_authenticated():

				if any([i in request.path for i in ['player_status', 'add_question', 'day_activate', 'all_questions', 'view_question']]) and not 'ohp' == request.user.username:
					return redirect('wordwars:home')
				try:
					day = view_kwargs['day']
				except:
					return None
				if day == None:
					return None
				day = get_object_or_404(Day, day_no=day)
				if not day.is_active:
					return redirect(reverse_lazy('wordwars:home'))
		else:
			if request.user.is_authenticated():
				if request.user.username == 'ohp':
					return redirect('wordwars:home')
				try:
					player = request.user.player
					logout(request)
					return None
				except:
					return None