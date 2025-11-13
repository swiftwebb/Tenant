
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from .views import *


# app_name = 'shop'


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', home, name='home'),
#     path('products/',product_list, name='product_list'),
#     path('products/<slug:slug>/',product_detail, name='productdet'),
#     path('add_to/<slug:slug>/',add_to, name='add_to'),
#     path('add/<slug:slug>/',add, name='add'),
#     path('remove_from/<slug:slug>/',remove_from, name='remove_from'),
#     path('remove/<slug:slug>/',remove, name='remove'),
#     path('remove_item/<slug:slug>/',remove_item, name='remove_item'),
#     path('remove_item/',remove_all, name='remove_all'),
#     path('ordersum/',cart_view, name='cart_view'),
#     path('checkout/',checkout, name='checkout'),
#     path("create_payment/", create_payment, name="create_payment"),
#     path("verify_payment/",verify_payment, name="verify_payment"),
#     path("ordderlist/",ordderlist, name="ordderlist"),
#     path("orderdet/<int:id>/",orderdet, name="orderdet"),
#     path("addcoupon/",addcoupon, name="addcoupon"),
#     path("search/",search, name="search"),
#     path('accounts/', include('allauth.urls')),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



