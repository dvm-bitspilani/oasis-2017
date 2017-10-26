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
	url(r'^show_level/(?P<level_id>\d+)/$', views.show_level, name="show_level"),
	url(r'^add_level/(?P<e_id>\d+)/$', views.event_levels_add, name="add_level"),
	url(r'^add_team/(?P<e_id>\d+)/$', views.add_delete_teams, name="add_team"),
    url(r'^teamdetails/(?P<e_id>\d+)/(?P<team_id>\d+)/$', views.team_details, name="team_details"),
    url(r'^teamdetails/(?P<e_id>\d+)/$', views.team_details_home, name="team_home"),
    url(r'^show_scores/(?P<e_id>\d+)/level-(?P<level_id>\d+)/$', views.show_scores, name='show_scores'),
    url(r'^update_scores/(?P<e_id>\d+)/level-(?P<level_id>\d+)/$', views.update_scores, name='update_scores'),
    # url(r'^select_winner/(?P<e_id>\d+)/$', views.select_winner, name='select_winner'),


    url(r'^add_bitsian/$', views.add_bitsian, name="add_bitsian"),
    url(r'^gen_emscode/$', views.gen_emscode, name='gen_emscode'),


	url(r'^add_judge/$', views.add_judge, name="add_judge"),
	url(r'^add_cd/$', views.add_cd, name="add_cd"),
	url(r'^events_controls/$', views.events_controls, name="events_controls"),
	url(r'^show_score_controls/(?P<e_id>\d+)/$', views.show_score_controls, name="show_score_controls"),

]
