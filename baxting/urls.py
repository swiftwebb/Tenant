
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from b_manager.views import *
from ecommerce.views import *
from blog.views import *
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from b_manager.sitemaps import StaticSitemap
from django.views.generic.base import TemplateView
sitemaps = {
    'static': StaticSitemap,
}
from django.http import HttpResponse

def robots_txt(request):
    content = """User-agent: *
Disallow:

Sitemap: https://{host}/sitemap.xml
"""
    return HttpResponse(
        content.format(host=request.get_host()),
        content_type="text/plain"
    )

urlpatterns = [
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    path('robots.txt', robots_txt),
    path('htjhtewhmdmtedtf/', admin.site.urls),
    path('', include('b_manager.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
