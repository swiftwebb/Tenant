from django.shortcuts import render, get_object_or_404,redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
# Create your views here.
import json
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django_tenants.utils import schema_context

from django.conf import settings

from b_manager.models import WebsiteVisit,Client



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt





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
    already_logged = WebsiteVisitertgerg.objects.filter(ip_address=ip_address).exists()

    if already_logged:
        return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

    # Save visit
    WebsiteVisitertgerg.objects.create(
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
    photo = Photo.objects.filter(featured=True).all().order_by('-id')
    return render(request, "booth/photo/home.html", {"photo":photo} )



@ratelimit(key='ip', rate='10/m', block=True)
def hoomelist(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    photos = Photo.objects.all().order_by('-id') 
    paginator = Paginator(photos, 24)            
    page_number = request.GET.get('page')
    home_page = paginator.get_page(page_number)
    return render(request, "booth/photo/homelist.html", {"home": home_page})






@ratelimit(key='ip', rate='10/m', block=True)
def hoomedet(request, id):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    photo = get_object_or_404(Photo, id=id)
    return render(request, "booth/photo/homedetail.html", {"photo":photo} )




@ratelimit(key='ip', rate='10/m', block=True)
def aboutme(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    photot = Myself.objects.all().order_by('-id')
    photo = photot.first()
    return render(request, "booth/photo/homeabout.html", {"photo":photo} )


@ratelimit(key='ip', rate='10/m', block=True)
def service(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    photo = Service_Photo.objects.all().order_by('-id')
    return render(request, "booth/photo/homeservice.html", {"photo":photo} )

@ratelimit(key='ip', rate='10/m', block=True)
def contact(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    if request.method == 'POST':
        name = request.POST.get('name')
        message = request.POST.get('message')
        email = request.POST.get('email')

        Bookings.objects.create(
            full_name=name,
            message=message,
            email=email,
        )
        send_mail(
            subject="Baxting's Website — New Client Message",
            message=f"""
        A potential client has just submitted a message on your website.

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

@ratelimit(key='ip', rate='10/m', block=True)
def about(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    return render(request, "booth/photo/homecontact.html", {} )




