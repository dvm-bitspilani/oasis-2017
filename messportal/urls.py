from django.conf.urls import url
from . import views
app_name = 'messportal'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^add_prof_show/$', views.add_prof_show, name='add_prof_show'),
	url(r'^add_mess_item/$', views.add_mess_item, name='add_mess_item'),
    url(r'^edit_item/(?P<i_id>\d+)/$', views.edit_item, name='edit_item'),
    url(r'^edit_profshow/(?P<ps_id>\d+)/$', views.edit_profshow, name='edit_profshow'),
	url(r'^create_mess_bill/$', views.create_mess_bill, name='create_mess_bill'),
	url(r'^create_profshow_bill/$', views.create_profshow_bill, name='create_profshow_bill'),
	url(r'^mess_bills/$', views.view_all_mess_bills, name='view_all_mess_bills'),
	url(r'^profshow_bills/$', views.view_all_profshow_bills, name='view_all_profshow_bills'),
	url(r'^mess_bill_details/(?P<mb_id>\d+)/$', views.mess_bill_details, name='mess_bill_details'),
	url(r'^profshow_bill_details/(?P<ps_id>\d+)$', views.profshow_bill_details, name='profshow_bill_details'),
    url(r'^mess_bill_receipt/(?P<mb_id>\d+)/$', views.mess_bill_receipt, name='mess_bill_receipt'),
	url(r'^profshow_bill_receipt/(?P<ps_id>\d+)$', views.profshow_bill_receipt, name='profshow_bill'),
    url(r'^delete_mess_bill/(?P<mb_id>\d+)/$', views.delete_mess_bill, name='delete_mess_bill'),
	url(r'^delete_profshow_bill/(?P<ps_id>\d+)$', views.delete_profshow_bill, name='delete_profshow_bill'),
]

