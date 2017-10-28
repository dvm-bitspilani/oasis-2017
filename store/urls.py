from django.conf.urls import url
from . import views

app_name = 'store'

urlpatterns = [
	
	url(r'^$', views.index, name='index'),
    url(r'^create_cart/$', views.create_cart, name='create_cart'),
    url(r'^cart_details/(?P<c_id>\d+)/$', views.cart_details, name='cart_details'),
    url(r'^item_details/(?P<c_id>\d+)/(?P<i_id>\d+)/$', views.item_details, name='item_details'),
    url(r'^add_item/(?P<c_id>\d+)/(?P<i_id>\d+)/$', views.add_item, name='add_item'),
    url(r'^combo_details/(?P<c_id>\d+)/(?P<co_id>\d+)/$', views.combo_details, name='combo_details'),
    url(r'^add_combo/(?P<c_id>\d+)/(?P<co_id>\d+)/$', views.add_combo, name='add_combo'),
    url(r'^make_cash_payment/(?P<c_id>\d+)/$', views.make_cash_payment, name='make_cash_payment'),
    url(r'^show_all_bills/$', views.show_all_bills, name='show_all_bills'),
    url(r'^bill_details/(?P<cb_id>\d+)/$', views.bill_details, name='bill_details'),
    url(r'^bill_receipt/(?P<cb_id>\d+)/$', views.bill_receipt, name='bill_receipt'),
    url(r'^delete_bill/(?P<cb_id>\d+)/$', views.delete_bill, name='delete_bill'),
    url(r'^make_online_payment/(?P<c_id>\d+)/$', views.make_online_payment, name='make_online_payment'),
    url(r'^payment_response/(?P<token>\w+)/$', views.payment_response, name='payment_response'),
    url(r'^api_request/$', views.api_request, name="api_request"),
	# ########## Basics #############
	# url(r'^contacts/$', views.contacts, name='contacts'),
	# url(r'^logout/$', views.user_logout, name='user-logout'),

]