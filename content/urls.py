from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homie, name='homie'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('service/', service, name='service'),
    path('portfolio/', portfolio, name='portfolio'),
    path('collab/', collab, name='collab'),
    path('collab/<int:id>', collabo, name='collabo'),
    path('cats/<int:id>/', cats, name='cats'),
    path("track_visit/", track_visit, name="track_visit"),
    
    path('accounts/', include('allauth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

