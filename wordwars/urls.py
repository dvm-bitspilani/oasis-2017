from django.conf.urls import url

url_patterns = [
	url(r'^$', views.home, name='home'),
	url(r'^play/(?P<day>\d+)/$', views.play, name='play'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^leaderboard$', views.leaderboard, name='leaderboard'),
	url(r'^instructions/$', views.instructions, name='instructions'),
	url(r'^rules/$', views.rules, name='rules'),
	url(r'^rulespage/$', views.rulespage, name='rulespage'),
	url(r'^contact/$', views.contact, name='contact'),

	]
