from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from . import views

app_name = 'api'

urlpatterns = [
		# url(r'^$', views.create_user, name="cr_approval"),
		url(r'^events/$', views.all_events, name="all_events"),
		url(r'^profshows/$', views.all_prof_shows, name="all_prof_shows"),
		url(r'^prof_show_part/(?P<part_barcode>\w+)/$', views.prof_show_part, name="prof_show_part"),
		url(r'^events/(?P<e_id>\d+)/$', views.get_event, name="get_event"),
		url(r'^api_token', obtain_jwt_token),
		url(r'^api_token_refresh', refresh_jwt_token),
		url(r'^get_profile/$', views.get_profile),
		url(r'^get_profile_bitsian/$', views.get_profile_bitsian),
		url(r'^add_prof_show/$', views.add_profshow),
		url(r'^validate_prof_show/$', views.validate_profshow),
		url(r'^get_events_cd/$', views.get_events_cd),
		url(r'^register_team/$', views.register_team),
]