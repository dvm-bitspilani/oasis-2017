from django.conf.urls import url
from shop import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

app_name = 'shop'

urlpatterns = [
			url(r'^api_token/?$', obtain_jwt_token, name="login"),
			url(r'^api_token_refresh/?$', refresh_jwt_token, name="refresh"),
			url(r'^api_token_verify/?$', verify_jwt_token),
			url(r'^create_wallet/?$', views.create_wallet, name="create_wallet"),
			url(r'^add_money_request/?$', views.add_money_request, name="add_money_request"),
			url(r'^add_money_response/?$', views.add_money_response, name="add_money_response"),
			url(r'^add_money_bitsian/?$', views.add_money_bitsian, name="add_money_bitsian"),
			url(r'^scan_user/?$', views.scan_qr_user, name="scan_user"),
			url(r'^transfer/?$', views.transfer_money, name="transfer"),
			# url(r'^transactions/?$', views.get_all_transactions, name="transaction_details"),
			# url(r'^transaction_details/(?P<t_id>\d+)/?$', views.transaction_details, name="transaction_details"),
			# url(r'^balance/?$', views.get_balance, name="balance"),
			url(r'^get_profile/?$', views.get_profile, name="get_profile"),
			url(r'^bt/?$', views.get_bt, name="get_bt"),
			url(r'^get_profile_bitsian/?$', views.get_profile_bitsian, name="get_profile_bitsian"),
			url(r'^get_stalls/?$', views.get_stalls),
			# url(r'^passbook/?$', views.get_all_transactions),
			url(r'^get_products/(?P<stall_id>\d+)/?$', views.get_products),
			# url(r'^get_product/?$', views.scan_qr_product),
			# url(r'^add/?$', views.add_to_cart),
			# url(r'^remove/?$', views.remove_from_cart),
			# url(r'^get_cart/?$', views.get_cart),
			# url(r'^checkout/?$', views.checkout),
			# url(r'^clear_cart/?$', views.clear_cart),
			url(r'^checkout_payment/?$', views.checkout_payment),
			url(r'^get_profshows/?$', views.get_profshows),
			url(r'^validate_profshow/?$', views.validate_profshow),
			url(r'^generate_code/?$', views.generate_code),
			
			url(r'^sales_today/?$', views.sales_today, name="sales_today"),
			url(r'^all_sales/?$', views.all_sales, name="all_sales"),
			url(r'^open_close/?$', views.open_close, name="open_close"),
			url(r'^available/?$', views.change_availability),
			url(r'^recieve_order/?$', views.recieve_order),
			url(r'^cancel_order/?$', views.cancel_order),
			url(r'^ready_order/?$', views.ready_order),
			url(r'^order_complete/?$', views.order_complete),

			url(r'^orders/?$', views.show_all_orders),
			url(r'^get_stall_id/?$', views.get_stall_id, name="get_stall_id"),
			url(r'^add_money_controls/?$', views.add_money_controls, name="add_money_controls"),

]