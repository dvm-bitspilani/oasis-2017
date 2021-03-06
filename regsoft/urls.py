from django.conf.urls import url
from . import views

app_name = 'regsoft'

urlpatterns = [
	
	url(r'^$', views.index, name='index'),
	########## Firewallz #############

	url(r'^firewallz/$', views.firewallz_home, name='firewallz_home'),
    url(r'^firewallz/(?P<c_id>\d+)/$', views.firewallz_approval, name='firewallz_approval'),
    url(r'^firewallz/groups/(?P<g_id>\d+)/$', views.get_group_list, name='get_group_list'),
	url(r'^firewallz/delete_group/(?P<g_id>\d+)/$', views.delete_group, name='delete_group'),
	url(r'^firewallz/add_guest/$', views.add_guest, name='add_guest'),
	url(r'^firewallz/add_participant/$', views.add_participant, name='add_participant'),
	url(r'^firewallz/remove_guests/$', views.remove_guests, name='remove_guests'),
	url(r'^firewallz/show_uploads/(?P<p_id>\d+)/$', views.show_uploads, name='show_uploads'),
	url(r'^controls/firewallz/profile_cards/(?P<g_id>\d+)/$', views.get_profile_card_group, name='get_profile_card_group'),
	# ########## RecNAcc #############
	url(r'^recnacc/$', views.recnacc_home, name='recnacc_home'),
	url(r'^recnacc/allocate/(?P<g_id>\d+)/$', views.allocate_participants, name='allocate_participants'),
	url(r'^recnacc/grouplist/(?P<c_id>\d+)/$', views.recnacc_group_list, name='recnacc_group_list'),
	url(r'^recnacc/group_vs_bhavan/$', views.group_vs_bhavan, name='group_vs_bhavan'),
	url(r'^recnacc/bhavans/$', views.recnacc_bhavans, name='recnacc_bhavans'),
	url(r'^recnacc/room_details/$', views.room_details, name='room_details'),
	url(r'^recnacc/bhavan_details/(?P<b_id>\d+)/$', views.bhavan_details, name='bhavan_details'),
	url(r'^recnacc/manage_vacancies/(?P<r_id>\d+)/$', views.manage_vacancies, name='manage_vacancies'),
    url(r'^recnacc/colleges/$', views.recnacc_college_details, name='recnacc_college_details'),
    url(r'^recnacc/college_detail/(?P<c_id>\d+)/$', views.college_detail, name='college_detail'),
	url(r'^recnacc/checkout/$', views.checkout_college, name="checkout_college"),
	url(r'^recnacc/checkout/(?P<c_id>\d+)/$', views.checkout, name="checkout"),
	url(r'^recnacc/checkout/groups/(?P<c_id>\d+)/$', views.checkout_groups, name="checkout_groups"),
	url(r'^recnacc/checkout/groupdetails/(?P<ck_id>\d+)/$', views.ck_group_details, name="ck_group_details"),
	url(r'^recnacc/checkout/master_checkout/$', views.master_checkout, name="master_checkout"),
	
	# ########## Controls #############
	url(r'^controls/$', views.controls_home, name='controls_home'),
	url(r'^controls/createbill/(?P<g_id>\d+)/$', views.create_bill, name='create_bill'),
    url(r'^controls/bills/$', views.show_all_bills, name='show_all_bills'),
	url(r'^controls/firewallz/profile_cards/$', views.get_profile_card, name='get_profile_card'),
	url(r'^controls/recnacc_list/$', views.recnacc_list, name='recnacc_list'),
	url(r'^controls/recnacc_list/(?P<g_id>\d+)/$', views.recnacc_list_group, name='recnacc_list_group'),
	url(r'^controls/generate_recnacc_list/$', views.generate_recnacc_list, name='generate_recnacc_list'),
	url(r'^controls/show_all_bills/$', views.show_all_bills, name='show_all_bills'),
	url(r'^controls/show_college_bills/(?P<c_id>\d+)/$', views.show_college_bills, name='show_college_bills'),
	url(r'^controls/bill_details/(?P<b_id>\d+)/$', views.bill_details, name='bill_details'),
	url(r'^controls/delete_bill/(?P<b_id>\d+)/$', views.delete_bill, name='delete_bill'),
	url(r'^controls/print_bill/(?P<b_id>\d+)/$', views.print_bill, name='print_bill'),

	# ########## FirewallzI #############
	url(r'^contacts/$', views.contacts, name='contacts'),
	url(r'^logout/$', views.user_logout, name='user-logout'),

]