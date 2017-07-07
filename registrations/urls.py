from django.conf.urls import url

from .views import *

urlpatterns = [
				url(r'^$', index, name="home"),
				url(r'^getlist/event/(?P<event>[\w\-]+)$', event_list, name="Event Excel Sheet"),
				url(r'^getlist/college/(?P<pk>[0-9]+)/$', college_list, name="College Excel Sheet"),
				]