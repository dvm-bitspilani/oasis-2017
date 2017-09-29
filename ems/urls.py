from django.conf.urls import url
from ems import views
app_name = 'ems'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.user_login, name="login"),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^events_select/$', views.events_select, name='events_select'),
	url(r'^event_home/(?P<e_id>\d+)/$', views.event_home, name="event_home"),
	url(r'^event_levels/(?P<e_id>\d+)/$', views.event_levels, name="event_levels"),
	url(r'^add_level/(?P<e_id>\d+)/$', views.event_levels_add, name="add_level"),
	url(r'^add_team/(?P<e_id>\d+)/$', views.add_team, name="add_team"),
    url(r'^teamdetails/(?P<e_id>\d+)/(?P<teamid>\d+)/$', views.team_details, name="team_details"),
    url(r'^teamdetails/(?P<e_id>\d+)/$', views.team_details_home, name="team_home"),
    url(r'^scores/(?P<e_id>\d+)/level-(?P<level>\d+)/$', views.scores_level, name='scores'),
    url(r'^select_winner/(?P<e_id>\d+)/$', views.select_winner, name='select_winner'),
]