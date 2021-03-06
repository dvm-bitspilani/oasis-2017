from django.conf.urls import url

from . import views

app_name = 'registrations'

urlpatterns = [
				url(r'^$', views.index, name="index"),
				url(r'^login/$', views.home, name="home"),
				url(r'^intro/$', views.prereg, name="prereg"),
				url(r'^getlist/event/(?P<event>[\w\-]+)$', views.event_list, name="Event Excel Sheet"),
				url(r'^upload_docs/$', views.upload_docs, name="upload_docs"),
				url(r'^payment/$', views.participant_payment, name="make_payment"),
				url(r'^approve/$', views.cr_approve, name="cr_approve"),
				url(r'^grouppayment/$', views.cr_payment, name="cr_payment"),
				url(r'^details/(?P<p_id>\d+)/$', views.participant_details, name="participant_details"),
				url(r'^profilecard/$', views.get_profile_card, name="get_profile_card"),
				url(r'^profilecard/(?P<p_id>\d+)/$', views.get_profile_card_cr, name="get_profile_card_cr"),
				url(r'^getqr/$', views.return_qr, name="generate_qr"),
				url(r'^getlist/college/(?P<pk>[0-9]+)/$', views.college_list, name="College Excel Sheet"),
				#url(r'^register/$', views.register, name="register"),
				url(r'^email_confirm/(?P<token>\w+)/$', views.email_confirm, name="email_confirm"),
				url(r'^payment_api_request', views.apirequest, name="API Request"),
				url(r'^manage_events/$', views.manage_events, name='manage_events'),
				]