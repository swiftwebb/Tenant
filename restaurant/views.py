from django.shortcuts import render, get_object_or_404,redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from datetime import date
from django_tenants.utils import schema_context

from django.core.mail import send_mail
from django.conf import settings

import json
from datetime import timedelta
from django.utils import timezone





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from b_manager.models import WebsiteVisit,Client


def get_client_ip(request):
    """Returns real visitor IP even behind proxy (Cloudflare, Nginx, Render etc)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()  # First IP = Real client
    return request.META.get("REMOTE_ADDR")


@csrf_exempt
def track_visit(request):
    if request.method != "POST":
        return JsonResponse({"status": "fail", "reason": "Method not allowed"}, status=405)

    # --- Validate Payload ---
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "fail", "reason": "Invalid JSON"}, status=400)

    tenant_id = data.get("tenant_id")
    if not tenant_id:
        return JsonResponse({"status": "fail", "reason": "No tenant_id"}, status=400)

    # --- Tenant Check ---
    try:
        tenant = Client.objects.get(id=tenant_id)
    except Client.DoesNotExist:
        return JsonResponse({"status": "fail", "reason": "Tenant not found"}, status=404)

    # --- Get Real IP ---
    ip_address = get_client_ip(request)

    # --- Optional Time Gate (avoid logging same visitor repeatedly for 24hrs) ---
    last_24 = timezone.now() - timedelta(hours=24)

    already_logged = WebsiteVisit.objects.filter(
        tenant=tenant,
        ip_address=ip_address,
        timestamp__gte=last_24
    ).exists()

    if already_logged:
        return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

    # --- Save Visit ---
    WebsiteVisit.objects.create(
        tenant=tenant,
        path=data.get("path", "/"),
        referrer=data.get("referrer", ""),
        user_agent=data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
        ip_address=ip_address,
    )

    return JsonResponse({"status": "success"})








@ratelimit(key='ip', rate='10/m', block=True)
def home(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    home = Hom.objects.all().first()

    return render(request, "ress/menu/home.html",{'home':home})



@ratelimit(key='ip', rate='10/m', block=True)
def book(request):
    today = date.today().isoformat()  # This is now safe

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        date_input = request.POST.get("date")  # rename this!
        time = request.POST.get("time")
        guests = request.POST.get("guests")
        special_requests = request.POST.get("special_requests", "")

        # Validate required fields
        if not all([name, email, phone, date_input, time, guests]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("book")

        Bookdbdbd.objects.create(
            name=name,
            email=email,
            phone=phone,
            date=date_input,
            time=time,
            guests=guests,
            special_requests=special_requests
        )
        send_mail(
            subject="Restaurant Website — New Booking Received",
            message=f"""
        A customer has just made a booking on your website. Below are their details:

        Name: {name}
        Email: {email}
        Phone: {phone}

        Date: {date_input}
        Time: {time}
        Number of Guests: {guests}

        Special Requests:
        {special_requests}

        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.tenant.email],
            fail_silently=False,
        )

        messages.success(request, "Your reservation has been submitted!")
        return redirect("book")

    return render(request, "ress/menu/book.html", {"today": today})


@ratelimit(key='ip', rate='10/m', block=True)
def menu(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    selected_category = request.GET.get("category", "main_courses")  # default

    categories = Catgg.objects.all()
    menu_items = Menu.objects.filter(category__name=selected_category)

    context = {
        "categories": categories,
        "items": menu_items,
        "selected_category": selected_category,
    }
    return render(request, "ress/menu/menu.html", context)
