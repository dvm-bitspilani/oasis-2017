from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
	url(r'^$', RedirectView.as_view(url='/2017/register')),	
    url(r'^admin/', admin.site.urls),
    url(r'^mirage/',include("preregistrations.urls")),
    url(r'^api/',include("api.urls")),
    url(r'^register/', include("registrations.urls")),
    url(r'^pcradmin/', include("pcradmin.urls")),
    url(r'^tarang/', include("tarang.urls")),
    url(r'^ems/', include("ems.urls")),
    url(r'^wordwars/', include("wordwars.urls")),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
