from django.conf.urls import url

from . import views

urlpatterns = [
				url(r'^$', views.index, name="index"),
				url(r'^getlist/event/(?P<event>[\w\-]+)$', views.event_list, name="Event Excel Sheet"),
				url(r'^getlist/college/(?P<pk>[0-9]+)/$', views.college_list, name="College Excel Sheet"),
				url(r'^register/$', views.register, name="register"),
				url(r'^email_confirm/(?P<token>\w+)/$', views.email_confirm, name="email_confirm"),
				url(r'^payment', views.apirequest, name="API Request"),
				]