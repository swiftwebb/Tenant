from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(DeliveryState)
admin.site.register(DeliveryCity)