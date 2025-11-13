
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *


app_name = 'shop'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('products/',product_list, name='product_list'),
    path('products/<slug:slug>/',product_detail, name='productdet'),
    path('remove_from/<slug:slug>/',remove_from, name='remove_from'),
    path('ordersum/',cart_view, name='cart_view'),
    path('add_to/<slug:slug>/',add_to, name='add_to'),
    path('remove/<slug:slug>/',remove, name='remove'),
    path('remove_item/<slug:slug>/',remove_item, name='remove_item'),
    path('remove_item/',remove_all, name='remove_all'),
    path('checkout/',checkout, name='checkout'),
    path("addcoupon/",addcoupon, name="addcoupon"),
    path("create_payment/", create_payment, name="create_payment"),
    path("verify_payment/",verify_payment, name="verify_payment"),
    path("search/",search, name="search"),
    path("removecoupon/",removecoupon, name="removecoupon"),
    path("ordderlist/",ordderlist, name="ordderlist"),
    path("orderdet/<int:id>/",orderdet, name="orderdet"),
    path("pickupform/",pickupform, name="pickupform"),
    path("paym/",paym, name="paym"),




    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
