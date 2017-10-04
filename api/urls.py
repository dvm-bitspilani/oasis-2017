from django.conf.urls import url

from . import views

urlpatterns = [
				# url(r'^$', views.create_user, name="cr_approval"),
				url(r'^events$', views.all_events, name="all_events"),
				url(r'^event/(?P<e_id>\d+)$', views.get_event, name="get_event"),

				]