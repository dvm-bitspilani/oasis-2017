from django.conf.urls import url
from tarang import views
app_name = 'tarang'

urlpatterns = [url(r'^$', views.index, name='index'),]