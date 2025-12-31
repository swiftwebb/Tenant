from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('yjrctyejrydtyrd/', admin.site.urls),
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('service/', service, name="service"),
    path('contact/', contact, name="contact"),
    path("track_visit/", track_visit, name="track_visit"),

        
    path('accounts/', include('allauth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
