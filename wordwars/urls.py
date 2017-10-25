from django.conf.urls import url
from wordwars import views
app_name = 'wordwars'

urlpatterns = [
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
	

	url(r'^add_question/$', views.add_question, name='add_question'),
	url(r'^day_activate/$', views.day_activate, name='day_activate'),
	url(r'^all_questions/$', views.all_questions, name='all_questions'),
	url(r'^view_question/(?P<q_id>\d+)/$', views.view_question, name="view_question"),
	]
