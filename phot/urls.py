
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *





urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('service/', service, name='service'),
    path('aboutme/', aboutme, name='aboutme'),
    path('contact/', about, name='about'),
    path('homelist/', hoomelist, name='hoomelist'),
    path('about/', contact, name='contact'),
    path("hoomedet/<int:id>/",hoomedet, name="hoomedet"),
    path("track_visit/", track_visit, name="track_visit"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
