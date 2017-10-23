from django.conf.urls import url
from . import views

app_name = 'regsoft'

urlpatterns = [
	
	url(r'^$', views.index, name='index'),
	# url(r'^test/$', views.home, name='home'),	
	#url(r'^get_barcode/$', views.get_barcode, name='get_barcode'),
	########## Firewallz #############

	url(r'^firewallz/$', views.firewallz_home, name='firewallz_home'),
    url(r'^firewallz/(?P<c_id>\d+)/$', views.firewallz_approval, name='firewallz_approval'),
    url(r'^firewallz/groups/(?P<g_id>\d+)/$', views.get_group_list, name='get_group_list'),
	url(r'^firewallz/delete_group/(?P<g_id>\d+)/$', views.delete_group, name='delete_group'),
	# url(r'^firewallz/edit/(?P<part_id>\d+)/$', views.firewallz_edit, name='firewallz_edit'),
	# url(r'^firewallz/add/(?P<gl_id>\d+)/$', views.firewallz_add, name='firewallz_add'),
	# url(r'^firewallz/delete/$', views.firewallz_delete, name='firewallz_delete'),
	# url(r'^firewallz/edit_tc/(?P<tc_id>\d+)/$', views.firewallz_edit_tc, name='firewallz_edit_tc'),
	# url(r'^firewallz/add_coach/(?P<gl_id>\d+)/$', views.add_coach_recnacc, name='add_coach_firewallz'),

	# ########## RecNAcc #############
	url(r'^recnacc/$', views.recnacc_home, name='recnacc_home'),
	url(r'^recnacc/allocate/(?P<g_id>\d+)/$', views.allocate_participants, name='allocate_participants'),
	url(r'^recnacc/grouplist/(?P<c_id>\d+)/$', views.recnacc_group_list, name='recnacc_group_list'),
	# url(r'^recnacc/add_coach/(?P<gl_id>\d+)/$', views.add_coach_recnacc, name='add_coach_recnacc'),
	# url(r'^recnacc/change/$',views.recnacc_change, name='change'),
	# url(r'^recnacc/college_vs_bhavan/$', views.college_vs_bhavan, name='college_vs_bhavan'),
	url(r'^recnacc/bhavans/$', views.recnacc_bhavans, name='recnacc_bhavans'),
	url(r'^recnacc/bhavan_details/(?P<b_id>\d+)/$', views.bhavan_details, name='bhavan_details'),
	url(r'^recnacc/manage_vacancies/(?P<r_id>\d+)/$', views.manage_vacancies, name='manage_vacancies'),
    url(r'^recnacc/colleges/$', views.recnacc_college_details, name='recnacc_college_details'),
	url(r'^recnacc/checkout/$', views.checkout_college, name="checkout_college"),
	url(r'^recnacc/checkout/(?P<c_id>\d+)/$', views.checkout, name="checkout"),
	url(r'^recnacc/checkout/groups/(?P<c_id>\d+)/$', views.checkout_groups, name="checkout_groups"),
	url(r'^recnacc/checkout/groupdetails/(?P<ck_id>\d+)/$', views.ck_group_details, name="ck_group_details"),
	
	# ########## Controls #############
	url(r'^controls/$', views.controls_home, name='controls_home'),
	url(r'^controls/createbill/(?P<g_id>\d+)/$', views.create_bill, name='create_bill'),
    url(r'^controls/bills/$', views.show_all_bills, name='show_all_bills'),
	url(r'^controls/profile_cards/$', views.get_profile_card, name='get_profile_card'),
    url(r'^controls/profile_cards/(?P<p_id>\d+)/$', views.get_profile_card_participant, name='get_profile_card_participant'),
	# url(r'^controlz/get_captains/$', views.get_captains, name='get_captains'),
	# url(r'^controlz/add_coach/(?P<gl_id>\d+)/$', views.add_coach_controlz, name='add_coach_controlz'),
	# url(r'^controlz/create_bill/(?P<gl_id>\d+)/$', views.create_bill, name='create_bill'),
	url(r'^controls/recnacc_list/$', views.recnacc_list, name='recnacc_list'),
	url(r'^controlz/recnacc_list/(?P<c_id>\d+)/$', views.recnacc_list_college, name='recnacc_list_college'),
	url(r'^controlz/generate_recnacc_list/$', views.generate_recnacc_list, name='generate_recnacc_list'),
	url(r'^controlz/show_all_bills/$', views.show_all_bills, name='show_all_bills'),
	url(r'^controlz/show_college_bills/(?P<c_id>\d+)/$', views.show_college_bills, name='show_college_bills'),
	url(r'^controlz/bill_details/(?P<b_id>\d+)/$', views.bill_details, name='bill_details'),
	url(r'^controlz/delete_bill/(?P<b_id>\d+)/$', views.delete_bill, name='delete_bill'),
	url(r'^controlz/print_bill/(?P<b_id>\d+)/$', views.print_bill, name='print_bill'),
	# url(r'^controlz/team_captain_list/$', views.team_captain_list, name='team_captain_list'),
	# url(r'^controlz/master_bill/$', views.master_bill, name='master_bill'),
	# # url(r'^controlz/view_captain_controlz/(?P<gl_id>\d+)/$', views.view_captain_controlz, name='view_captain_controlz'),
	# url(r'^controlz/edit/(?P<part_id>\d+)/$', views.controlz_edit, name='controlz_edit'),
	# url(r'^controlz/add/(?P<gl_id>\d+)/$', views.controlz_add, name='controlz_add'),
	# url(r'^controlz/delete/$', views.controlz_delete, name='controlz_delete'),
	# url(r'^controlz/event_details/$', views.get_details, name='get_details'),
	# url(r'^controlz/edit_tc/(?P<tc_id>\d+)/$', views.controlz_edit_tc, name='controlz_edit_tc'),
	# url(r'^controlz/all_bills/$',views.all_bills, name="all_bills"),

	# ########## FirewallzI #############
	# #url(r'^firewallzi/$', views.firewallzi_home, name='firewallzi-home')
	url(r'^contacts/$', views.contacts, name='contacts'),
	# url(r'^logout/$', views.user_logout, name='user-logout'),
	# url(r'^controller/$', views.fuckup),

]