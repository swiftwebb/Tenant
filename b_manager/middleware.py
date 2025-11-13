# # middleware.py
# from .models import Client

# class TenantStatusMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         tenant = getattr(request, 'tenant', None)
#         if tenant:
#             tenant.update_status()
#         return self.get_response(request)
# from django.http import HttpResponse


from django.shortcuts import render



class TenantStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)


   

        if tenant:
            # Dynamically assign URLconf based on tenant
            if not getattr(tenant, "live", False):
                return render(request, "under_construction.html", status=503)
            if hasattr(tenant, 'urlconf') and tenant.urlconf:
                request.urlconf = tenant.urlconf
                print(request.urlconf)  # use tenant's custom URLconf
            else:
                request.urlconf = 'ecom.urls'  # fallback default

            tenant.update_status()  # your existing logic

        return self.get_response(request)









# middleware.py
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant
import cloudinary

class CloudinaryTenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant = get_tenant(request)
        if tenant and tenant.cloud_name and tenant.api_key and tenant.api_secret:
            cloudinary.config(
                cloud_name=tenant.cloud_name,
                api_key=tenant.api_key,
                api_secret=tenant.api_secret,
                secure=True
            )
        return None
