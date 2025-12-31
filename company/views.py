from django.shortcuts import render,redirect
from .models import *
# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 

from b_manager.models import WebsiteVisit
from django.core.mail import send_mail
from django.conf import settings


import json
from datetime import timedelta
from django.utils import timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from django_ratelimit.decorators import ratelimit
from b_manager.models import WebsiteVisit,Client


def get_client_ip(request):
    """Returns real visitor IP even behind proxy (Cloudflare, Nginx, Render etc)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()  # First IP = Real client
    return request.META.get("REMOTE_ADDR")


# @csrf_exempt
# def track_visit(request):
#     if request.method != "POST":
#         return JsonResponse({"status": "fail", "reason": "Method not allowed"}, status=405)

#     # --- Validate Payload ---
#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "fail", "reason": "Invalid JSON"}, status=400)

#     tenant_id = data.get("tenant_id")
#     if not tenant_id:
#         return JsonResponse({"status": "fail", "reason": "No tenant_id"}, status=400)

#     # --- Tenant Check ---
#     try:
#         tenant = Client.objects.get(id=tenant_id)
#     except Client.DoesNotExist:
#         return JsonResponse({"status": "fail", "reason": "Tenant not found"}, status=404)

#     # --- Get Real IP ---
#     ip_address = get_client_ip(request)

#     # --- Optional Time Gate (avoid logging same visitor repeatedly for 24hrs) ---
#     last_24 = timezone.now() - timedelta(hours=24)

#     already_logged = WebsiteVisit.objects.filter(
#         tenant=tenant,
#         ip_address=ip_address,
#         timestamp__gte=last_24
#     ).exists()

#     if already_logged:
#         return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

#     # --- Save Visit ---
#     WebsiteVisit.objects.create(
#         tenant=tenant,
#         path=data.get("path", "/"),
#         referrer=data.get("referrer", ""),
#         user_agent=data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
#         ip_address=ip_address,
#     )

#     return JsonResponse({"status": "success"})




@csrf_exempt
def track_visit(request):
    if request.method != "POST":
        return JsonResponse({"status": "fail", "reason": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "fail", "reason": "Invalid JSON"}, status=400)

    ip_address = get_client_ip(request)

    # Check if visit already logged
    if request.user.is_authenticated:
        already_logged = WebsiteVisitgthberbr.objects.filter(user=request.user).exists()
    else:
        already_logged = WebsiteVisitgthberbr.objects.filter(ip_address=ip_address).exists()

    if already_logged:
        return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

    # Save visit
    WebsiteVisitgthberbr.objects.create(
        user=request.user if request.user.is_authenticated else None,
        path=data.get("path", "/"),
        referrer=data.get("referrer", ""),
        user_agent=data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
        ip_address=ip_address,
    )

    return JsonResponse({"status": "success"})














@ratelimit(key='ip', rate='10/m', block=True) 
def home(request):
    home = Ideal.objects.all().first()
    service = Serv.objects.filter(premium=True).order_by('-id')
    context={
        'home':home,
        'service':service,
    }
    return render(request,"comp/compan/home.html", context)

@ratelimit(key='ip', rate='10/m', block=True) 
def about(request):
    about = Abut.objects.all().first()
    lead = Leaders.objects.all()
    context={
        'lead':lead,
        'about':about,
    }
    return render(request,"comp/compan/about.html", context)

@ratelimit(key='ip', rate='10/m', block=True) 
def service(request):
    service = Serv.objects.all().order_by('-id')
    context={
        'service':service,
    }
    return render(request,"comp/compan/service.html", context)


@ratelimit(key='ip', rate='10/m', block=True) 
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        email = request.POST.get('email')

        Imes.objects.create(
            name=name,
            message=message,
            email=email,
            phone=phone,
        )
        send_mail(
            subject="New Message from Your Website",
            message=f"""
        You have received a new message from a potential client.

        Name: {name}
        Email: {email}
        Phone: {phone}

        Message:
        {message}
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.tenant.email],
            fail_silently=False,
        )


        messages.success(request, "Message recieved, We will get back to you shortly")
        return redirect('contact')
    return render(request, "comp/compan/contact.html", {} )

