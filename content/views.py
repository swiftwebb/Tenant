from django.shortcuts import render, redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django_ratelimit.decorators import ratelimit

# === HOME PAGE ===
from django.core.mail import send_mail

import json
from datetime import timedelta
from django.utils import timezone

from django.conf import settings


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

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "fail", "reason": "Invalid JSON"}, status=400)

    ip_address = get_client_ip(request)

    # Check if visit already logged
    already_logged = WebsiteVisiterggssfe.objects.filter(ip_address=ip_address).exists()

    if already_logged:
        return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

    # Save visit
    WebsiteVisiterggssfe.objects.create(
        path=data.get("path", "/"),
        referrer=data.get("referrer", ""),
        user_agent=data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
        ip_address=ip_address,
    )

    return JsonResponse({"status": "success"})










@ratelimit(key='ip', rate='7/m', block=True)
def homie(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    home = Home.objects.all().order_by('-id')
    homes = home.first()
    return render(request, 'con/content/homie.html', {'homes': homes})


# === ABOUT PAGE ===
@ratelimit(key='ip', rate='7/m', block=True)
def about(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    home = About.objects.all().order_by('-id')
    homes = home.first()
    return render(request, 'con/content/about.html', {'homes': homes})


# === CONTACT FORM ===
@ratelimit(key='ip', rate='7/m', block=True)
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        message = request.POST.get('message')
        email = request.POST.get('email')

        Mess.objects.create(
            name=name,
            messages=message,
            email=email,
        )
        send_mail(
            subject="Baxting's Website — New Client Message",
            message=f"""
        A potential client has just submitted a message through your website. Below are the details:

        Name: {name}
        Email: {email}

        Message:
        {message}
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.tenant.email],
            fail_silently=False,
        )

        messages.success(request, "Message recieved, We will get back to you shortly")
        return redirect('about')
    return redirect('about')


@ratelimit(key='ip', rate='7/m', block=True)
def portfolio(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    category_slug = request.GET.get('category', None)
    categories = Categorysss.objects.all()

    home = Socails.objects.all().order_by('-id')
    if category_slug:
        home = home.filter(category__slug=category_slug)

    paginator = Paginator(home, 400)
    page_number = request.GET.get('page')
    home_page = paginator.get_page(page_number)

    return render(request, 'con/content/port.html', {
        'home': home_page,
        'categories': categories
    })



@ratelimit(key='ip', rate='7/m', block=True)
def cats(request, id):
    category = Categorysss.objects.filter(pk=id).first()
    if not category:
        return redirect('portfolio')

    homes = Socails.objects.filter(category=category).order_by('-id')

    return render(request, 'con/content/cats.html', {
        'category': category,
        'homes': homes
    })

@ratelimit(key='ip', rate='7/m', block=True)
def collab(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    home = Campagin.objects.all().order_by('-id')
    return render(request, 'con/content/coll.html', {'home': home})

@ratelimit(key='ip', rate='7/m', block=True)
def collabo(request, id):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    home= Campagin.objects.filter(pk=id).first()


    return render(request, 'con/content/collab.html', {'home': home})
    

@ratelimit(key='ip', rate='7/m', block=True)
def service(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    home = Service.objects.all().order_by('-id')
    return render(request, 'con/content/service.html', {'home': home})
