from django.shortcuts import render,redirect
from .models import *
# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 

from django.db.models import Q

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from b_manager.models import WebsiteVisit,Client
import json
from datetime import timedelta
from django.utils import timezone

from django_ratelimit.decorators import ratelimit
from django.core.mail import send_mail


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
        already_logged = WebsiteViwreger.objects.filter(user=request.user).exists()
    else:
        already_logged = WebsiteViwreger.objects.filter(ip_address=ip_address).exists()

    if already_logged:
        return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

    # Save visit
    WebsiteViwreger.objects.create(
        user=request.user if request.user.is_authenticated else None,
        path=data.get("path", "/"),
        referrer=data.get("referrer", ""),
        user_agent=data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
        ip_address=ip_address,
    )

    return JsonResponse({"status": "success"})



















@ratelimit(key='ip', rate='5/m', block=True)  # 5 attempts per minute per IP
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")  # successful login
        else:
            context = {"error": "Invalid username or password."}
            return render(request, "login.html", context)

    return render(request, "login.html")





@ratelimit(key='ip', rate='10/m', block=True)
def homm(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    blog = Blog.objects.filter(featured=True).order_by("-id").first()
    recent = Blog.objects.all().order_by("-id")[:3]
    context = {
        'blog': blog,
        'recent':recent 
    }
    return render(request, "blog/blogs/bhome.html", context )


@ratelimit(key='ip', rate='10/m', block=True)
def blogdet(request, slug):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    blog = Blog.objects.filter(slug=slug).first()

    recent = Blog.objects.exclude(slug=slug).order_by("-id")[:3]

    context = {
        'blog': blog,
        'recent': recent
    }
    return render(request, "blog/blogs/bdet.html", context)




@ratelimit(key='ip', rate='10/m', block=True)
@login_required
def post_comment(request, slug):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    blog = get_object_or_404(Blog, slug=slug)

    if request.method == "POST":
        text = request.POST.get("comment")

        if text.strip() != "":
            # Create comment
            new_comment = Comm.objects.create(
                name=request.user,
                comment=text
            )

            # Attach comment to blog
            blog.comment.add(new_comment)

        return redirect('det', slug=slug)

    return redirect('det', slug=slug)


@ratelimit(key='ip', rate='10/m', block=True)
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comm, id=pk)

    # ⭐ Only the person who wrote the comment can delete
    if comment.name != request.user:
        messages.error(request, "You are not allowed to delete this comment.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Find the blog the comment belongs to
    blog = Blog.objects.filter(comment=comment).first()

    if blog:
        blog.comment.remove(comment)

    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect('det', slug=blog.slug)



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
    blog = Abbb.objects.all().first()
    context = {
        'blog': blog,
    }
    return render(request, "blog/blogs/about.html", context )


@ratelimit(key='ip', rate='10/m', block=True)
def blogall(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    blog_list = Blog.objects.all().order_by("-id")  # all blogs ordered by newest first

    # Paginate: 6 blogs per page
    paginator = Paginator(blog_list, 9)  
    page_number = request.GET.get('page')  # get current page from query params
    page_obj = paginator.get_page(page_number)  # returns Page object

    context = {
        'blog': page_obj,  # use 'blog' in template, like your other context
    }
    return render(request, "blog/blogs/ball.html", context)








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

        Msg.objects.create(
            name=name,
            message=message,
            email=email,
        )
        send_mail(
            subject="New Contact Form Message",
            message=f"""
        A new message has been submitted through your blog contact form.

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
        return redirect('contact')
    return render(request, "blog/blogs/contact.html", {} )

@ratelimit(key='ip', rate='10/m', block=True)
def search(request):
    tenant = request.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
    queryset = Blog.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)

        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'blog/blogs/search.html', context)



@ratelimit(key='ip', rate='10/m', block=True)
def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if email already exists
        if Sub.objects.filter(email=email).exists():
            messages.warning(request, 'You are already subscribed!')
        else:
            # Create new subscription
            Sub.objects.create(email=email)
            messages.success(request, 'Thank you for subscribing! You will receive updates soon.')
        
        return redirect('hoom')  # Redirect back to home page
    
    # If GET request, redirect to home
    return redirect('hoom')