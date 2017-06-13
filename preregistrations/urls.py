from django.conf.urls import url

from .views import *
urlpatterns = [
				url(r'^$', index, name="home"),
				url(r'^payment', apirequest, name="API Request"),
				url(r'^getlist', get_excel_sheet)
				]