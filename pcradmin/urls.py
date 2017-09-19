from django.conf.urls import url
from pcradmin import views
app_name = 'pcradmin'

urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^college/$', views.college, name='college'),
	url(r'^college_rep/(?P<id>\d+)/$', views.select_college_rep, name='select_college_rep'),
	url(r'^verify_profile/(?P<part_id>\d+)/$', views.verify_profile, name='verify_profile'),
	url(r'^logout/$', views.user_logout, name='user-logout'),


	url(r'^contacts/$', views.contacts, name='contacts'),

]

