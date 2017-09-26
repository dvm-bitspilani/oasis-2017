from django.conf.urls import url
from ems import views
app_name = 'ems'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.user_login, name="login"),
	url(r'^events_select/$', views.events_select, name='events_select'),
	url(r'^events_home/(?P<e_id>\d+)/$', views.events_home, name="events_home"),
	url(r'^add_team/$', views.add_team, name="add_team"),
	url(r'^add_bitsian_team/$', views.add_bitsian_team, name="add_bitsian_team"),
]

