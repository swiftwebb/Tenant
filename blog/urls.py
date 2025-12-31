from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

app_name = 'blog'

urlpatterns = [
    path('hthedfgdmftdtm/', admin.site.urls),
    path('', homm, name="hoom"),

    path('contact/', contact, name="contact"),
    path('about/', about, name="about"),
    path('search/', search, name="search"),
    path('bloglist/', blogall, name="blogall"),
    path('subscribe/', subscribe, name='subscribe'),
    path('delete_comment/<int:pk>/', delete_comment, name='delete_comment'),
    path('blog/<slug:slug>', blogdet, name="det"),
    path('post_comment/<slug:slug>', post_comment, name="post_comment"),
    path("track_visit/", track_visit, name="track_visit"),


        
    path('accounts/', include('allauth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
