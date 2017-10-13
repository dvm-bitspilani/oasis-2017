from django.conf.urls import url
from pcradmin import views
app_name = 'pcradmin'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^college/$', views.college, name='college'),
	url(r'^college_rep/(?P<id>\d+)/$', views.select_college_rep, name='select_college_rep'),
	url(r'^approve_participations/(?P<id>\d+)/$', views.approve_participations, name='approve_participations'),
	url(r'^verify_profile/(?P<part_id>\d+)/$', views.verify_profile, name='verify_profile'),
	url(r'^add_college/$', views.add_college, name='add_college'),
	url(r'^stats/$', views.stats, name='stats'),
	url(r'^stats/(?P<order>\w+)/$', views.stats, name='stats'),
	url(r'^stats_event/(?P<e_id>\d+)/$', views.stats_event, name='stats_event'),
	url(r'^final_confirmation/$', views.view_final, name='view_final'),
	url(r'^final_email/(?P<eg_id>\d+)$', views.final_email, name='final_email'),
	url(r'^download_pdf/(?P<eg_id>\d+)$', views.download_pdf, name='download_pdf'),
	url(r'^final_confimation/(?P<c_id>\d+)/$', views.final_confirmation, name='final_confirmation'),
	url(r'^master_stats/$', views.master_stats, name='master_stats'),
	url(r'^logout/$', views.user_logout, name='user-logout'),
	url(r'^contacts/$', views.contacts, name='contacts'),
	url(r'^stats_event/(?P<e_id>\d+)/(?P<c_id>\d+)/$', views.stats_event_college, name='stats_event_college'),
]

