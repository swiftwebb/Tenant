from django.shortcuts import render, redirect,get_object_or_404,HttpResponse
from django.conf import settings
import json
from .models import *
import requests
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import *
from datetime import timedelta, date
from .models import Client, Domain
from django.utils import timezone
from django.contrib import messages
from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from content.models import *
import os
from phot.models import *
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import hmac
import hashlib
from django.db.models import Prefetch
import openai
import os
from company.models import *
from blog.models import *
from ecom.models import *
from content.models import *
from phot.models import *
from django.core.files.base import ContentFile
from urllib.parse import urlparse
from restaurant.models import *

from django.core.mail import send_mail
from django.conf import settings


from functools import wraps
from b_manager.models import Client

from django_ratelimit.decorators import ratelimit

import requests
PLAN_PRIORITY = {
    'free': 1,
    'basic': 2,
    'premium': 3,
}

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


# def get_client_ip(request):
#     """Returns real visitor IP even behind proxy (Cloudflare, Nginx, Render etc)."""
#     forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
#     if forwarded:
#         return forwarded.split(",")[0].strip()  # First IP = Real client
#     return request.META.get("REMOTE_ADDR")


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







def activate_tenant_domain(tenant):
    schema_name = tenant.schema_name

    # Deactivate all old domains
    Domain.objects.filter(tenant=tenant).update(is_primary=False)

    # Get the existing domain for this tenant
    domain = Domain.objects.filter(tenant=tenant).first()
    
    # If a domain exists, make it primary
    if domain:
        domain.is_primary = True
        domain.save(update_fields=["is_primary"])
        return domain
    
    # If no domain exists yet, return None (domain will be created later in fom view)
    return None

def tenant_ip_key(group, request):
    tenant = getattr(request, 'tenant', None)
    tenant_id = getattr(tenant, 'schema_name', 'public')
    ip = request.META.get('REMOTE_ADDR', '')
    return f"{tenant_id}:{ip}"


# @ratelimit(key='ip', rate='15/m', block=True)
@ratelimit(key='ip', rate='15/m', block=True)
def hhh(request):
    user_review = None
    if request.user.is_authenticated:
        client = Client.objects.filter(user=request.user).first()
        if client:
            user_review = Review.objects.filter(name=client).first()

    review = Review.objects.all()
    about = Tutorial.objects.all().first()

    return render(request, "customers/home.html", {
        "about": about,
        "review": review,
        "user_review": user_review,
    })







@ratelimit(key='ip', rate='15/m', block=True)
def tutt(request):
    tut = Tutorial.objects.all()


    return render(request, "customers/tut.html", {
        "tut": tut,
    })








@ratelimit(key='ip', rate='15/m', block=True)
@login_required
@csrf_exempt
def delete_review(request):
    if request.method == "POST":
        client = Client.objects.filter(user=request.user).first()
        if client:
            review = Review.objects.filter(name=client).first()
            if review:
                review.delete()
                return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def submit_review(request):
    if request.method == "POST":
        client = Client.objects.get(user=request.user)
        comment = request.POST.get("comment")
        rating = request.POST.get("rating")

        review, created = Review.objects.get_or_create(name=client)
        review.comment = comment
        review.rating = rating
        review.save()

        return JsonResponse({"success": True, "created": created})

    return JsonResponse({"success": False})








def onboarding_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # If user is not authenticated, redirect to login
        if not request.user.is_authenticated:
            return redirect('login')

        # Get the client linked to this user
        client = Client.objects.filter(name=request.user.username).first()
        if not client:
            messages.info(request, "Please choose a plan to get started.")
            return redirect('customers:plan_list')

        # Step 1: Must have a plan
        if not client.plan:
            messages.info(request, "Please choose a plan to continue.")
            return redirect('customers:plan_list')

        # Step 2: Must have selected job type
        if not client.job_type:
            messages.info(request, "Please select your business type.")
            return redirect('customers:job_list')

        # Step 3: Must have chosen a website template
        if not client.template_type:
            messages.info(request, "Please choose a website template.")
            return redirect('customers:web_sel')

        # Step 4: Must have filled out form
        if not client.business_name:
            messages.info(request, "Please complete your business setup.")
            return redirect('customers:formad')

        return view_func(request, *args, **kwargs)
    return _wrapped_view












PAYSTACK_INITIALIZE_URL = settings.PAYSTACK_INITIALIZE_URL

@ratelimit(key='ip', rate='15/m', block=True)
def create_trial_tenant(request, plan):
    user = request.user
    """Create or update a 7-day trial tenant for the Basic plan."""
    schema_name = user.username.lower()
    trial_end_date = date.today() + timedelta(days=7)

    tenant, created = Client.objects.get_or_create(
        schema_name=schema_name,
        defaults={
            'name': user.username,
            'email': user.email,
            'is_active': True,
            'trial_ends_on': trial_end_date,
            'has_used_trial': True,
            'plan': plan,
        }
    )

    # 🔹 Link tenant to user
    request.user.tenant = tenant
    request.user.save()


    # 🔄 If tenant already existed but has no active trial, update it
    if not created:
        if not tenant.has_used_trial:
            tenant.trial_ends_on = trial_end_date
            tenant.has_used_trial = True
            tenant.plan = plan
            tenant.is_active = True
            tenant.save()

            activate_tenant_domain(tenant)
        else:
            # Already used trial once before
            return None

    # ✅ Create domain if missing
    # Domain.objects.get_or_create(
    #     domain=f"{schema_name}.baxting.com",
    #     tenant=tenant,
    #     is_primary=True
    # )

    return tenant



@ratelimit(key='ip', rate='15/m', block=True)
def plan_list(request):
    plans = SubscriptionPlan.objects.all().order_by('price')
    return render(request, 'customers/pricing.html', {'plans': plans})








@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def job_list(request):
    client = Client.objects.filter(name=request.user.username).first()

    if not client or client.plan is None:
        messages.warning(request, "Please log in and choose a plan")
        return redirect('customers:plan_list')

    if client.job_type is not None:
        messages.warning(request, "You've already chosen a job type")
        return redirect('customers:web_sel')

    PLAN_PRIORITY = {'free': 1, 'basic': 2, 'premium': 3}
    user_level = PLAN_PRIORITY.get(client.plan.name.lower(), 1)

    jobs = Job.objects.all().order_by('name')
    jobs = [job for job in jobs if PLAN_PRIORITY[job.min_plan] <= user_level]

    return render(request, 'customers/jobsel.html', {'jobs': jobs})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def jjob(request):

    if request.method != 'POST':
        return redirect('customers:plan_list')
    
    job_id = request.POST.get('job_id')

    joob = get_object_or_404(Job, pk=job_id)
    schema_name = request.user.username.lower()
    tenant, created = Client.objects.get_or_create(
    schema_name=schema_name,
    defaults={
                'name': request.user.username,
                'email': request.user.email,
                'is_active': True,
            }
        )

    tenant.job_type = joob
    tenant.save()


    
    return redirect('customers:web_sel')









@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def upgrade_init(request):
    if request.method != 'POST':
        return redirect('customers:plan_list')
    
    plan_id = request.POST.get('plan_id')
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    payer_email = request.user.email if request.user.is_authenticated else request.POST.get('email')

    if not payer_email:
        return redirect('customers:plan_list')

        # Get tenant
    tenant = request.user.tenant
    if tenant and tenant.paystack_subscription_code:
        resp = cancel_paystack_subscription(tenant.paystack_subscription_code, tenant.paystack_email_token)
        print("Cancel old subscription response:", resp)

        if resp.get('status'):
            # Mark old subscription as non-renewing in your DB
            tenant.auto_renew = False
            tenant.is_active = False
            tenant.paystack_subscription_code = None
            tenant.paystack_email_token = None
            tenant.save(update_fields=['auto_renew','is_active','paystack_subscription_code','paystack_email_token'])
        else:
            # Could not cancel → show message or handle error
            print("Failed to cancel old subscription:", resp.get('message'))
                # Optionally alert admin/user



    # 🟢 Free Plan (no payment, no trial)
    if plan.name == 'Free':
        schema_name = request.user.username.lower()
        tenant, created = Client.objects.get_or_create(
            schema_name=schema_name,
            defaults={
                'name': request.user.username,
                'email': request.user.email,
                'is_active': True,
            }
        )
        request.user.tenant = tenant
        request.user.save()

        tenant.plan = plan
        tenant.trial_ends_on = None
        tenant.paid_until = None
        tenant.is_active = True
        tenant.free = True
        tenant.paystack_subscription_code = None  # Clear any existing subscription
        tenant.save()
        activate_tenant_domain(tenant)

        return render(request, 'customers/tksub.html', {
            'message': 'Free plan activated successfully!',
            'plan': plan
        })
    
    # 🔵 Basic Plan (7-day free trial)
    elif plan.name == 'Basic':
        tenant = None # create_trial_tenant(request, plan)
        if not tenant:
            # Trial already used - go to paid subscription
            paystack_plan_code = plan.plan_code

            metadata = {
                'tenant': getattr(request, 'tenant', None).schema_name if hasattr(request, 'tenant') else request.user.username.lower(),
                'plan_name': plan.name,
            }

            payload = {
                'email': payer_email,
                'amount': int(plan.price * 100),
                'plan': paystack_plan_code,  # THIS CREATES A SUBSCRIPTION
                'metadata': json.dumps(metadata),
                'callback_url': request.build_absolute_uri(reverse('customers:paystack_verify'))
            }

            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json'
            }

            resp = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers, timeout=15)
            data = resp.json()

            if not data.get('status'):
                return render(request, 'customers/tksub.html', {
                    'error': 'Failed to initialize payment', 'plan': plan
                })

            authorization_url = data['data']['authorization_url']
            return redirect(authorization_url)

        return render(request, 'customers/tksub.html', {
            'message': f'Your 7-day free trial has started and ends on {tenant.trial_ends_on}.',
            'plan': plan
        })

    # 🔴 Premium Plan (paid with auto-renewal)
    else:
        paystack_plan_code = plan.plan_code

        metadata = {
            'tenant': getattr(request, 'tenant', None).schema_name if hasattr(request, 'tenant') else request.user.username.lower(),
            'plan_name': plan.name,
        }

        payload = {
            'email': payer_email,
            'amount': int(plan.price * 100),
            'plan': paystack_plan_code,  # THIS CREATES A SUBSCRIPTION
            'metadata': json.dumps(metadata),
            'callback_url': request.build_absolute_uri(reverse('customers:paystack_verify'))
        }

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        resp = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers, timeout=15)
        data = resp.json()

        if not data.get('status'):
            return render(request, 'customers/tksub.html', {
                'error': 'Failed to initialize payment', 'plan': plan
            })

        authorization_url = data['data']['authorization_url']
        return redirect(authorization_url)


# ============================================
# 3. UPDATE paystack_verify VIEW - KEY CHANGES HERE
# ============================================

@ratelimit(key='ip', rate='15/m', block=True)
def paystack_verify(request):
    reference = request.GET.get('reference')
    if not reference:
        return render(request, 'customers/tksub.html', {'error': 'Missing transaction reference'})

    headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
    verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
    resp = requests.get(verify_url, headers=headers, timeout=15)
    data = resp.json()

    if data.get('status') and data['data']['status'] == 'success':
        metadata = data['data'].get('metadata', {})
        plan_name = metadata.get('plan_name')
        tenant_name = metadata.get('tenant')

        # Get customer and authorization details
        customer_code = data['data']['customer']['customer_code']
        authorization = data['data']['authorization']
        authorization_code = authorization.get('authorization_code')  # This is what we need
        
        plan = SubscriptionPlan.objects.filter(name=plan_name).first()
        if not plan:
            return render(request, 'customers/tksub.html', {'error': 'Plan not found'})

        schema_name = request.user.username.lower()

        tenant, created = Client.objects.get_or_create(
            schema_name=schema_name,
            defaults={
                'name': request.user.username,
                'email': request.user.email,
                'is_active': True,
                'trial_ends_on': None,
                'has_used_trial': True,
                'plan': plan,
            }
        )
        
        request.user.tenant = tenant
        request.user.save()

        # ✅ FETCH SUBSCRIPTION CODE FROM PAYSTACK
        subscription_code = None
        
        # Method 1: Check if subscription_code is in the transaction data
        if 'subscription' in data['data'] and data['data']['subscription']:
            subscription_code = data['data']['subscription'].get('subscription_code')
        
        # Method 2: If not in transaction, fetch from subscriptions endpoint
        if not subscription_code:
            try:
                subscription_url = 'https://api.paystack.co/subscription'
                subscription_params = {'customer': customer_code, 'plan': plan.plan_code}
                sub_resp = requests.get(subscription_url, headers=headers, params=subscription_params, timeout=15)
                sub_data = sub_resp.json()
                
                if sub_data.get('status') and sub_data.get('data'):
                    subscriptions = sub_data['data']
                    # Get the most recent active subscription
                    for sub in subscriptions:
                        if sub.get('status') == 'active':
                            subscription_code = sub.get('subscription_code')
                            break
            except Exception as e:
                print(f"Error fetching subscription: {e}")

        # Update tenant with subscription info
        tenant.plan = plan
        tenant.paid_until = timezone.now() + timedelta(days=plan.duration_days)
        tenant.is_active = True
        tenant.paystack_customer_code = customer_code
        tenant.paystack_subscription_code = subscription_code  # May be None initially
        tenant.paystack_email_token = authorization_code  # Use authorization_code instead
        tenant.auto_renew = True
        tenant.save()
        
        activate_tenant_domain(tenant)

        # Log for debugging
        print(f"Subscription created - Code: {subscription_code}, Customer: {customer_code}, Auth: {authorization_code}")

        return render(request, 'customers/tksub.html', {
            'message': f'Payment successful! {plan.name} plan activated for {tenant.name}. Auto-renewal is enabled.',
            'plan': plan
        })

    return render(request, 'customers/tksub.html', {'error': 'Payment verification failed.'})

# ============================================
# 4. ENHANCED paystack_webhook - HANDLES AUTOMATIC RENEWALS
# ============================================






@ratelimit(key='ip', rate='15/m', block=True)
@csrf_exempt
def paystack_webhook(request):
    try:
        raw = request.body.decode("utf-8")
        print("=== PAYSTACK WEBHOOK ===")
        print(raw)

        payload = json.loads(raw)
        event = payload.get("event")
        data = payload.get("data", {})

        customer_obj = data.get("customer", {})
        customer_email = customer_obj.get("email")
        customer_code = customer_obj.get("customer_code")

        if not customer_email and not customer_code:
            return JsonResponse({"status": "no customer info"}, status=200)

        # Try to fetch tenant by email first
        tenant = Client.objects.filter(email=customer_email).first() if customer_email else None
        # Fallback: fetch by customer_code
        if not tenant and customer_code:
            tenant = Client.objects.filter(paystack_customer_code=customer_code).first()

        if not tenant:
            print("Tenant not found yet for customer:", customer_email, customer_code)
            return JsonResponse({"status": "tenant not found"}, status=200)

        # Use tenant's schema for django-tenants
        with schema_context(tenant.schema_name):

            # -----------------------------
            # 1️⃣ subscription.create → Save subscription code and email token
            # -----------------------------
            if event == "subscription.create":
                sub_code = data.get("subscription_code")
                email_token = data.get("email_token")
                paystack_customer_code = customer_obj.get("customer_code")

                tenant.paystack_subscription_code = sub_code
                tenant.paystack_email_token = email_token
                tenant.paystack_customer_code = paystack_customer_code
                tenant.is_active = True
                tenant.auto_renew = True
                tenant.save(update_fields=[
                    "paystack_subscription_code",
                    "paystack_email_token",
                    "paystack_customer_code",
                    "is_active",
                    "auto_renew"
                ])
                print(f"Saved subscription code {sub_code} for tenant {tenant.schema_name}")
                return JsonResponse({"status": "subscription created"}, status=200)

            # -----------------------------
            # 2️⃣ invoice.create → Update subscription info if Paystack rotates subscription codes
            # -----------------------------
            if event == "invoice.create":
                sub_obj = data.get("subscription", {})
                sub_code = sub_obj.get("subscription_code")
                email_token = sub_obj.get("email_token")

                if sub_code:
                    tenant.paystack_subscription_code = sub_code
                    tenant.paystack_email_token = email_token
                    tenant.save(update_fields=["paystack_subscription_code", "paystack_email_token"])
                    print(f"Updated subscription code {sub_code} for tenant {tenant.schema_name}")
                return JsonResponse({"status": "invoice processed"}, status=200)

            # -----------------------------
            # 3️⃣ charge.success → Update paid_until and activate tenant
            # -----------------------------
            if event == "charge.success":
                plan_data = data.get("plan", {})
                plan_code = plan_data.get("plan_code")
                plan = SubscriptionPlan.objects.filter(plan_code=plan_code).first()

                if plan:
                    tenant.paid_until = timezone.now().date() + timedelta(days=plan.duration_days)
                    tenant.is_active = True
                    tenant.auto_renew = True
                    tenant.save(update_fields=["paid_until", "is_active", "auto_renew"])
                    print(f"charge.success: renewed, paid_until set to {tenant.paid_until}")
                return JsonResponse({"status": "charge processed"}, status=200)

            # -----------------------------
            # 4️⃣ subscription.disable → Disable tenant subscription
            # -----------------------------
            if event == "subscription.disable":
                tenant.is_active = False
                tenant.auto_renew = False
                tenant.paystack_subscription_code = None
                tenant.save(update_fields=["is_active", "auto_renew", "paystack_subscription_code"])
                print(f"subscription.disable fired for tenant {tenant.schema_name}")
                return JsonResponse({"status": "subscription disabled"}, status=200)

        return JsonResponse({"status": "ignored"}, status=200)

    except Exception as e:
        print("Webhook error:", str(e))
        return JsonResponse({"status": "error", "message": str(e)}, status=500)







def cancel_paystack_subscription(subscription_code, email_token=None):
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {'code': subscription_code}
    if email_token:
        payload['token'] = email_token

    try:
        resp = requests.post('https://api.paystack.co/subscription/disable',
                             json=payload, headers=headers, timeout=15)
        data = resp.json()
        return data
    except requests.RequestException as e:
        return {'status': False, 'message': str(e)}















# ============================================
# 5. KEEP YOUR update_tenants_status CRON JOB
# ============================================
# This is still needed to deactivate tenants after grace period ends



def update_tenants_status(request):
    today = timezone.now().date()

    for tenant in Client.objects.all():
        # expired
        if tenant.paid_until and tenant.paid_until < today:
            tenant.is_active = False
            tenant.live = False
            tenant.save(update_fields=['is_active','live'])
            Domain.objects.filter(tenant=tenant).update(is_primary=False)
            continue

        # valid
        if tenant.paid_until and tenant.paid_until >= today:
            tenant.is_active = True
            tenant.save(update_fields=['is_active'])
            continue
        if tenant.paid_until==None and not tenant.free:

            tenant.is_active = False
            tenant.live = False
            tenant.save(update_fields=['is_active','live'])
            Domain.objects.filter(tenant=tenant).update(is_primary=False)
            continue

    return HttpResponse("Tenant status update completed.")


# ============================================
# 6. OPTIONAL: Add a view to let users cancel subscription
# ============================================

@ratelimit(key='ip', rate='15/m', block=True)
@login_required
@require_POST
def cancel_subscription(request):
    """
    Allow users to cancel their auto-renewal on Paystack.
    """

    client = request.user.tenant
    if client.plan:
        client.plan = None
        client.save()
    tenant = getattr(request.user, 'tenant', None)

    if not tenant or not tenant.paystack_subscription_code:
        messages.error(request, "No active subscription found.")
        return redirect('customers:dashboard')

    if request.method == 'POST':
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        disable_url = 'https://api.paystack.co/subscription/disable'

        payload = {
            'code': tenant.paystack_subscription_code,
    'token': tenant.paystack_email_token
        }

        try:
            resp = requests.post(disable_url, json=payload, headers=headers, timeout=15)
            data = resp.json()
            print("Paystack disable response:", data)  # Debugging

            if data.get('status'):
                # Successfully disabled
                tenant.auto_renew = False
                tenant.save(update_fields=['auto_renew'])
                messages.success(
                    request,
                    "Auto-renewal cancelled. Your plan will remain active until the end of your billing period."
                )
            else:
                # Failed to disable → show reason from Paystack
                error_msg = data.get('message', 'Unknown error')
                messages.error(request, f"Failed to cancel subscription: {error_msg}")

        except requests.RequestException as e:
            print("Paystack request error:", str(e))
            messages.error(request, "Network error: Could not reach Paystack API.")

        return redirect('customers:dashboard')

    # GET request → show confirmation page
    return render(request, 'customers/cancel_subscription.html', {'tenant': tenant})






























































@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def web_temp(request):
    

    client = Client.objects.filter(name=request.user.username).first()
    if not client or client.plan is None:
        messages.warning(request, "Please log in and choose a plan")
        return redirect('customers:plan_list')

    if client.template_type is not None:
        return redirect('customers:formad')
    
    if client.job_type is None:

        return redirect('customers:job_list')
    
    if client.job_type and client.template_type:
        return redirect('customers:formad')
    # Determine what templates they can see based on plan
    plan_name = client.plan.name.lower() if client.plan else "free"
    job_category = client.job_type.name.lower() if client.job_type else None
    print(f"Filtering templates for job_category='{job_category}'")

    # Base queryset for all templates
    templates = WebsiteTemplate.objects.all()

    # Filter templates by user's job type (if set)
    if job_category:
        templates = templates.filter(category__iexact=job_category)

    # Filter by plan access
    if plan_name == "free":
        templates = templates.filter(min_plan__iexact="free")
    elif plan_name == "basic":
        templates = templates.filter(min_plan__in=["free", "basic"])
    elif plan_name == "premium":
        # Premium users see all templates
        templates = templates
    else:
        # Default safe fallback (only free templates)
        templates = templates.filter(min_plan__iexact="free")

    # Order by name for neatness
    templates = templates.order_by('name')

    return render(request, 'customers/templselection.html', {
        'websites': templates,
        'plan': plan_name,
        'job_category': job_category
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def web_temp_detail(request, slug):

    webs = get_object_or_404(WebsiteTemplate, slug=slug)

    return render(request, 'customers/templatepreview.html', {'webs': webs})


@ratelimit(key='ip', rate='15/m', block=True) 
@login_required
def web_welected(request):

    if request.method != 'POST':
        return redirect('customers:job_list')
    web_id =  request.POST.get('web_id')

    webb = get_object_or_404(WebsiteTemplate, pk=web_id)
    schema_name = request.user.username.lower()
    tenant, created = Client.objects.get_or_create(
    schema_name=schema_name,
    defaults={
                'name': request.user.username,
                'email': request.user.email,
                'is_active': True,
            }
        )

    tenant.template_type = webb
    tenant.save()
    
    return redirect('customers:formad')




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def setts(request):
    client = Client.objects.filter(name=request.user.username).first()

    if client.plan is None:
        messages.info(request, "Please select a plan.")
        return redirect('customers:plan_list')
    if not client.job_type or client.job_type.name is None:
        messages.info(request, "Please select a category")
        return redirect('customers:job_list')
    if not client.template_type or client.template_type.name is None:
        messages.info(request, "Please select a template")
        return redirect('customers:web_sel')
    if not client.business_name or client.business_name is None:
        messages.info(request, "Please fill the form")
        return redirect('customers:formad')

    webname = client.job_type.svg_url
    jtype = client.job_type.name
    job_name = client.job_type.name

    # Select correct form
    form_map = {
        'Store': StoreForm,
        'Restaurant': RestForm,
        'Freelancer': FreeForm,
        'Influencers': influForm,
        'Photo Artist': PhotoForm,
        'Company': CompanyForm,
        'Blogger': BlogForm,
        'Food Vendor': FoodtForm,
    }

    form_class = form_map.get(job_name)
    if not form_class:
        return HttpResponse('Contact support: info@baxting.com')

    # Initialize form
    form = form_class(instance=client)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=client)
        
        if form.is_valid():
            client = form.save(commit=False)
            client.bank = form.cleaned_data.get("bank")
            client.bank_name = form.cleaned_data.get("bank_name")
            client.save()

            send_mail(
                subject=f"New Form Submission from {client.business_name}",
                message=f"""
        A user just submitted their details.

        Name: {request.user.username}
        Business Name: {client.business_name}
        Job Type: {client.job_type.name}
        """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['info@baxting.com'],   # <-- your email here
                fail_silently=False,
            )

            if not client.business_name:
                messages.error(request, "Please enter a business name to create a domain or choose another business name.")
                return render(request, 'customers/det.html', {'form': form, 'webname': webname, 'jtype': jtype})

            business_slug = slugify(client.business_name)
            domain_name = f"{business_slug}.baxting.com"
            client.save()

            Domain.objects.update_or_create(
                tenant=client,
                defaults={"domain": domain_name, "is_primary": True}
            )

            messages.success(request, f"Your business details have been saved successfully! Domain: {domain_name}, it takes 5 minutes- 24 hours to rectify changes")
            return redirect('customers:myweb')
        else:

            messages.error(request, "Please correct the errors below and try again.")


    return render(request, 'customers/dett.html', {
        'form': form,
        "webname": webname,
        'jtype': jtype,
    })







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def fom(request):
    client = Client.objects.filter(name=request.user.username).first()

    if not client or client.plan is None:
        messages.warning(request, "Please log in and choose a plan")
        
        return redirect('customers:plan_list')

    if client.job_type is None:
        return redirect('customers:web_sel')

    webname = client.job_type.svg_url
    jtype = client.job_type.name
    job_name = client.job_type.name

    # Select correct form
    form_map = {
        'Store': StoreForm,
        'Restaurant': RestForm,
        'Freelancer': FreeForm,
        'Influencers': influForm,
        'Photo Artist': PhotoForm,
        'Company': CompanyForm,
        'Blogger': BlogForm,
        'Food Vendor': FoodtForm,
    }

    form_class = form_map.get(job_name)
    if not form_class:
        return HttpResponse('Contact support: info@baxting.com')

    # Initialize form
    form = form_class(instance=client)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=client)
        
        if form.is_valid():
            client = form.save(commit=False)
            client.bank = form.cleaned_data.get("bank")
            client.bank_name = form.cleaned_data.get("bank_name")
            client.save()
            send_mail(
                subject=f"New Form Submission from {client.business_name}",
                message=f"""
        A user just submitted their details.

        Name: {request.user.username}
        Business Name: {client.business_name}
        Job Type: {client.job_type.name}
        """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['info@baxting.com'],   # <-- your email here
                fail_silently=False,
            )
            if not client.business_name:
                messages.error(request, "Please enter a business name to create a domain or choose another business name.")
                return render(request, 'customers/det.html', {'form': form, 'webname': webname, 'jtype': jtype})

            business_slug = slugify(client.business_name)
            domain_name = f"{business_slug}.baxting.com"
            client.save()

            Domain.objects.update_or_create(
                tenant=client,
                defaults={"domain": domain_name, "is_primary": True}
            )

            messages.success(request, f"Your business details have been saved successfully!")
            return redirect('customers:myweb')
        else:

            messages.error(request, "Please correct the errors below and try again.")

    if client.business_name:
        return redirect('customers:dashboard')

    return render(request, 'customers/det.html', {
        'form': form,
        "webname": webname,
        'jtype': jtype,
    })




@ratelimit(key='ip', rate='15/m', block=True)
def about(request):

    return render(request, 'customers/about.html', {})



@ratelimit(key='ip', rate='15/m', block=True)
def help(request):
    return render(request, 'customers/help.html', {})




@ratelimit(key='ip', rate='15/m', block=True)
def terms(request):
    return render(request, 'customers/tems.html', {})


@ratelimit(key='ip', rate='15/m', block=True)
def privacy(request):
    return render(request, 'customers/privacyr.html', {})


@ratelimit(key='ip', rate='15/m', block=True)
def switch(request):
    client = Client.objects.filter(name=request.user.username).first()

    if not client or client.plan is None:
        messages.warning(request, "Please log in and choose a plan")
        
        return redirect('customers:plan_list')
    subscription = client.plan
    bbb = timezone.now()

    return render(request, 'customers/subb.html', {'subscription':subscription,'client':client, 'bbb':bbb})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_p(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from ecom.models import Product

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Product.objects.all())
        for p in products:
            p.image_url = p.image.url if p.image else None

    return render(request, 'customers/productlist.html', {
        'tenant': tenant,
        'products': products,
    })































@ratelimit(key='ip', rate='15/m', block=True)
def verify_bank_account(request):
    bank_code = request.GET.get('bank')
    account_number = request.GET.get('account_no')

    if not bank_code or not account_number:
        return JsonResponse({'status': 'error', 'message': 'Missing bank or account number'})

    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    # print(data)
    

    if data.get('status'):
        return JsonResponse({
            'status': 'success',
            'account_name': data['data']['account_name']
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid details'})












@ratelimit(key='ip', rate='15/m', block=True)
@onboarding_required
@login_required
def dashboard(request):
    client = get_object_or_404(Client, name=request.user.username)

  
        



    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        messages.info(request, "Please select a plan to activate your account.")
        return redirect('customers:plan_list')




    if client.plan is None:
        messages.info(request, "Please select a plan.")
        return redirect('customers:plan_list')
    if not client.job_type or client.job_type.name is None:
        messages.info(request, "Please select a category")
        return redirect('customers:job_list')
    if not client.template_type or client.template_type.name is None:
        messages.info(request, "Please select a template")
        return redirect('customers:web_sel')
    if not client.business_name or client.business_name is None:
        messages.info(request, "Please fill the form")
        return redirect('customers:formad')
    if client.live is False:

        messages.info(request, "Please wait till your website is live")
        return redirect('customers:myweb')

 
    job_name = client.job_type.name if client.job_type else None
    if job_name == 'Store':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from ecom.models import Product, Order, Sale
            products = list(Product.objects.all())
            order = list(Order.objects.select_related('address').filter(Paid=True).all())
            Sales =  list(Sale.objects.all())
            visit = list(WebsiteVisitgrtghbr.objects.all())
        return render(request, 'customers/dashboard.html',{'products':products,'order':order, 'client':client, 'sales':Sales,'visit':visit})
    if job_name == 'Influencers' or job_name == 'Freelancer':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from content.models import Mess
            products = list(Mess.objects.all())
            visit = list(WebsiteVisiterggssfe.objects.all())
        return render(request, 'customers/dashboard_content.html',{'products':products, 'client':client,'visit':visit})
    if job_name == 'Photo Artist':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from phot.models import Bookings
            products = list(Bookings.objects.all())
            visit = list(WebsiteVisitertgerg.objects.all())
        return render(request, 'customers/dashboard_photo.html',{'products':products, 'client':client,'visit':visit})


    if job_name == 'Company':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from company.models import Imes
            products = list(Imes.objects.all())
            visit = list(WebsiteVisitgthberbr.objects.all())
        return render(request, 'customers/dashboard_company.html',{'products':products, 'client':client,'visit':visit})

    
    if job_name == 'Restaurant':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from restaurant.models import Bookdbdbd
            products = list(Bookdbdbd.objects.all())
        return render(request, 'customers/dashboardrr.html',{'products':products, 'client':client,})
    
    if job_name == 'Blogger':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from blog.models import Msg
            products = list(Msg.objects.all())
            visit = list(WebsiteViwreger.objects.all())
        return render(request, 'customers/dashboard_blog.html',{'products':products, 'client':client,'visit':visit})
    
    
    else:
        messages.success(request,"No dashboard available right now for you")
        return redirect('customers:home')



@ratelimit(key='ip', rate='15/m', block=True)
@onboarding_required
@login_required
def website(request):
    client = get_object_or_404(Client, name=request.user.username)
    clients = client.live
    domain = get_object_or_404(Domain, tenant=client)

    if client.plan is None:
        return redirect('customers:plan_list')
    if not client.job_type or client.job_type.name is None:
        return redirect('customers:job_list')
    if not client.template_type or client.template_type.name is None:
        return redirect('customers:web_sel')
    if not client.business_name or client.business_name is None:
        return redirect('customers:formad')
    return render(request, 'customers/mywebsite.html', {
        'clients': clients,
        'domain': domain,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@onboarding_required
@login_required
def domn(request):
    client = get_object_or_404(Client, name=request.user.username)
    clients = client.live
    domain = get_object_or_404(Domain, tenant=client)

    if client.plan is None:
        return redirect('customers:plan_list')
    if not client.job_type or client.job_type.name is None:
        return redirect('customers:job_list')
    if not client.template_type or client.template_type.name is None:
        return redirect('customers:web_sel')
    if not client.business_name or client.business_name is None:
        return redirect('customers:formad')
    return render(request, 'customers/domain.html', {
        'clients': clients,
        'domain': domain,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def transaction(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from ecom.models import Order,Trans
        # force evaluation into a list
        order = list(
    Trans.objects.select_related('order', 'order__address')
    .order_by('-order__ordered_date')
)


    return render(request, 'customers/trans.html', {
        'tenant': tenant,
        'order': order,
    })









# for ManyToManyField
# @login_required
# def product_detail_d(request, pk):
#     tenant = request.user.tenant

#     with schema_context(tenant.schema_name):
#         from ecommerce.models import Product  # ✅ import inside context
#         product = get_object_or_404(Product.objects.prefetch_related('category'), pk=pk)



#     return render(request, 'customers/productdetails.html', {'product': product})










@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def product_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from ecom.models import Product
        product = get_object_or_404(Product.objects.select_related('category'), pk=pk)

    return render(request, 'customers/productdetails.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def product_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import Product
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Product, pk=pk)

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:product_detail_d', pk=product.pk)
        else:
            form = ProductForm(instance=product, tenant=tenant)

        return render(request, 'customers/produpdate.html', {'form': form, 'product': product})




# @login_required
# def dashboard_products(request):
#     tenant = getattr(request.user, 'tenant', None)

#     if not tenant:
#         return redirect('customers:plan_list')

#     with schema_context(tenant.schema_name):
#         from dashboard.models import Product
#         products = Product.objects.all()

#     return render(request, 'dashboard/products.html', {'products': products})

@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_product(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:product_detail_d', pk=product.pk)
        else:
            form = ProductForm(tenant=tenant)

        return render(request, 'customers/producreate.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_product(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, pk=pk)

        if request.method == 'POST':
            product.delete()
            return redirect('customers:dashboard_p')  # redirect to your product list page

    # Optional: render a confirmation page before deleting
    return redirect('customers:delete_p', pk=product.pk)


@ratelimit(key='ip', rate='15/m', block=True)
def delete_p(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, pk=pk)

    return render(request, 'customers/del_p.html',{'product':product})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_orderlist(request):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from ecom.models import Order
        # force evaluation into a list
        order = list(
            Order.objects.select_related('address')
            .filter(Paid=True)
            .order_by('-ordered_date')
        )

    return render(request, 'customers/orderlist.html', {
        'tenant': tenant,
        'order': order,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
@require_POST
def mark_order_delivered(request, order_id):
    tenant = request.user.tenant
    with schema_context(tenant.schema_name):
        from ecom.models import Order, Sale,Product

        order = get_object_or_404(Order, pk=order_id)

 

        # Calculate total cost of all products in the cart
        total_cost = sum(
            cart_item.product.cost * cart_item.quantity 
            for cart_item in order.cart.all()
        )
        if order.amount > 166667:
            amount_after_fee = order.amount - 5000
        else:

            amount_after_fee = 0.97 * order.amount


        # Create Sale record
        if order.status == "shipping (payment on delivery)":
            sale = Sale.objects.create(
            cost=total_cost,
            amount= order.amount,
            total= order.amount - total_cost,
            reference=order.ref_code
        )
        if order.status == "shipping":  

            sale = Sale.objects.create(
            cost=total_cost,
            amount= amount_after_fee,
            total= amount_after_fee - total_cost,
            reference=order.ref_code
        )

        # Add products from cart to Sale
        for cart_item in order.cart.all():
            sale.product.add(cart_item.product)
        
        for cart_item in order.cart.all():
            product = cart_item.product
            if product.quantity >= cart_item.quantity:
                product.quantity -= cart_item.quantity
                product.save()
            else:
                # Just in case — avoid negative stock
                product.quantity = 0
                product.save()

               # Mark order delivered
        order.status = 'delivered'
        order.save()



    return redirect('customers:order_detail_d', pk=order_id)


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def order_detail_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import Order, Sale, Cart, Product

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        queryset = (
            Order.objects
            .select_related('address', 'user', 'coupon')
            .prefetch_related(
                'cart__product',
                'cart__product__category'
            )
        )
        order = get_object_or_404(queryset, pk=pk)
        cart_items = order.cart.all()

        # 🧮 Calculate totals
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        total_discount = sum(
            (item.product.price - (item.product.discount_price or item.product.price)) * item.quantity
            for item in cart_items
        )

        # 🏷️ Promo / coupon discount
        promo_discount = order.coupon.amount if order.coupon else 0

        # 💰 Grand total = total - discounts - promo
        grand_total = total_price - total_discount - promo_discount
        if grand_total < 0:
            grand_total = 0 

    return render(request, 'customers/Orderdedt.html', {'order': order,
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'promo_discount': promo_discount,
        'grand_total': grand_total,})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_order(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        order = get_object_or_404(Order, pk=pk)

        order.delete()
    
    return redirect('customers:dashboard_orderlist')  
    



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_couponlist(request):
    tenant = request.user.tenant 
    coupon = []

   
    with schema_context(tenant.schema_name):
        from ecom.models import Coupon
        coupon = list(Coupon.objects.all())

    return render(request, 'customers/couponlist.html', {
        'tenant': tenant,
        'coupon': coupon,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def coupon_detail_d(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import Coupon  # ✅ import inside context
        coupon = get_object_or_404(Coupon, pk=pk)

    return render(request, 'customers/coupondet.html', {'coupon': coupon})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_coupon(request):
    tenant = request.user.tenant  # get current user's tenant

    with schema_context(tenant.schema_name):
        if request.method == 'POST':
            form = CouponForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                coupon = form.save()
                return redirect('customers:coupon_detail_d', pk=coupon.pk)
        else:
            form = CouponForm(tenant=tenant)

        return render(request, 'customers/couponcreate.html', {'form': form})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def coupon_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import Coupon
    from django.shortcuts import get_object_or_404, redirect, render

    with schema_context(tenant.schema_name):
        coupon = get_object_or_404(Coupon, pk=pk)

        if request.method == 'POST':
            form = CouponForm(request.POST, request.FILES, instance=coupon, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:coupon_detail_d', pk=coupon.pk)
        else:
            form = CouponForm(instance=coupon, tenant=tenant)

        return render(request, 'customers/couponupd.html', {'form': form, 'coupon': coupon})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_coupon(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        coupon = get_object_or_404(Coupon, pk=pk)

        coupon.delete()
    
    return redirect('customers:dashboard_couponlist')  
    


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_catlist(request):
    tenant = request.user.tenant 
    coupon = []

   
    with schema_context(tenant.schema_name):
        from ecom.models import Category
        category = list(Category.objects.all())

    return render(request, 'customers/categoryl.html', {
        'tenant': tenant,
        'category': category,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def category_detail_d(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import Category  # ✅ import inside context
        category = get_object_or_404(Category, pk=pk)

    return render(request, 'customers/catrgoryd.html', {'category': category})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_cat(request):
    tenant = request.user.tenant  # get current user's tenant

    with schema_context(tenant.schema_name):
        if request.method == 'POST':
            form = CatForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                category = form.save()
                return redirect('customers:category_detail_d', pk=category.pk)
        else:
            form = CatForm(tenant=tenant)

        return render(request, 'customers/catgoryc.html', {'form': form})

@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def cat_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import Category
    from django.shortcuts import get_object_or_404, redirect, render

    with schema_context(tenant.schema_name):
        category = get_object_or_404(Category, pk=pk)

        if request.method == 'POST':
            form = CatForm(request.POST, request.FILES, instance=category, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:category_detail_d', pk=category.pk)
        else:
            form = CatForm(instance=category, tenant=tenant)

        return render(request, 'customers/categoryu.html', {'form': form, 'category': category})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_cat(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Category, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_catlist')  
    




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_del(request):
    tenant = request.user.tenant

    
    return render(request,'customers/Delivery.html',{})  
    


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_del_other(request):
    tenant = request.user.tenant

    # Fetch & evaluate inside schema context
    with schema_context(tenant.schema_name):
        delivery = list(DeliveryState.objects.exclude(name__icontains='lagos'))

    return render(request, 'customers/deliveryo.html', {
        'tenant': tenant,
        'delivery': delivery,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def delivery_detail_d(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import DeliveryState  # ✅ import inside context
        category = get_object_or_404(DeliveryState, pk=pk)

    return render(request, 'customers/deliveryd.html', {'category': category})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_del(request):
    tenant = request.user.tenant  # get current user's tenant

    with schema_context(tenant.schema_name):
        if request.method == 'POST':
            form = DelStateForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                category = form.save()
                return redirect('customers:delivery_detail_d', pk=category.pk)
        else:
            form = DelStateForm(tenant=tenant)

        return render(request, 'customers/deliveryc.html', {'form': form})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def del_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import DeliveryState
    from django.shortcuts import get_object_or_404, redirect, render

    with schema_context(tenant.schema_name):
        category = get_object_or_404(DeliveryState, pk=pk)

        if request.method == 'POST':
            form = DelStateForm(request.POST, request.FILES, instance=category, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:delivery_detail_d', pk=category.pk)
        else:
            form = DelStateForm(instance=category, tenant=tenant)

        return render(request, 'customers/lagu.html', {'form': form, 'category': category})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_del(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(DeliveryState, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_del_other')  
    




# @ratelimit(key=tenant_ip_key, rate='40/m', block=True)
# @login_required
# def dashboard_del_lag(request):
#     tenant = request.user.tenant

#     # Fetch & evaluate inside schema context
#     with schema_context(tenant.schema_name):
#         delivery = list(DeliveryCity.objects.select_related('state'))

#     return render(request, 'customers/lagl.html', {
#         'tenant': tenant,
#         'delivery': delivery,
#     })






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_del_lag(request):
    tenant = request.user.tenant

    # Fetch & evaluate inside schema context
    with schema_context(tenant.schema_name):
        delivery = list(DeliveryBase.objects.all())

    return render(request, 'customers/lagl2.html', {
        'tenant': tenant,
        'delivery': delivery,
    })






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def delivery_detail_lag(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import DeliveryBase  # ✅ import inside context
        category = get_object_or_404(DeliveryBase, pk=pk)

    return render(request, 'customers/lagd2.html', {'category': category})





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def lag_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import DeliveryBase
    from django.shortcuts import get_object_or_404, redirect, render

    with schema_context(tenant.schema_name):
        category = get_object_or_404(DeliveryBase, pk=pk)

        if request.method == 'POST':
            form = DelBaseForm(request.POST, request.FILES, instance=category, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:delivery_detail_lag', pk=category.pk)
        else:
            form = DelBaseForm(instance=category, tenant=tenant)

        return render(request, 'customers/lagu2.html', {'form': form, 'category': category})









# @ratelimit(key=tenant_ip_key, rate='40/m', block=True)
# @login_required
# def delivery_detail_lag(request, pk):
#     tenant = request.user.tenant

#     with schema_context(tenant.schema_name):
#         from ecom.models import DeliveryCity  # ✅ import inside context
#         category = get_object_or_404(DeliveryCity, pk=pk)

#     return render(request, 'customers/lagd.html', {'category': category})


# @ratelimit(key=tenant_ip_key, rate='40/m', block=True)
# @login_required
# def lag_edit_d(request, pk):
#     tenant = request.user.tenant

#     from django_tenants.utils import schema_context
#     from ecom.models import DeliveryCity
#     from django.shortcuts import get_object_or_404, redirect, render

#     with schema_context(tenant.schema_name):
#         category = get_object_or_404(DeliveryCity, pk=pk)

#         if request.method == 'POST':
#             form = DelCityForm(request.POST, request.FILES, instance=category, tenant=tenant)
#             if form.is_valid():
#                 form.save()
#                 return redirect('customers:delivery_detail_lag', pk=category.pk)
#         else:
#             form = DelCityForm(instance=category, tenant=tenant)

#         return render(request, 'customers/lagu.html', {'form': form, 'category': category})

# @ratelimit(key=tenant_ip_key, rate='40/m', block=True)
# @login_required
# def dashboard_create_lag(request):
#     tenant = request.user.tenant  # get current user's tenant

#     with schema_context(tenant.schema_name):
#         if request.method == 'POST':
#             form = DelCityForm(request.POST, request.FILES, tenant=tenant)
#             if form.is_valid():
#                 category = form.save()
#                 return redirect('customers:delivery_detail_lag', pk=category.pk)
#         else:
#             form = DelCityForm(tenant=tenant)

#         return render(request, 'customers/lagc.html', {'form': form})



# @ratelimit(key=tenant_ip_key, rate='40/m', block=True)
# @login_required
# def dashboard_delete_lag(request, pk):
#     tenant = request.user.tenant

#     with schema_context(tenant.schema_name):
#         cat = get_object_or_404(DeliveryCity, pk=pk)

#         cat.delete()
    
#     return redirect('customers:dashboard_del_lag')  
    






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_pcon(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Socails

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Socails.objects.all().order_by('-id'))
        for p in products:
            p.thumbnail_url = p.thumbnail.url if p.thumbnail else None

    return render(request, 'customers/post.html', {
        'tenant': tenant,
        'products': products,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def con_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import Socails
        product = get_object_or_404(Socails.objects.select_related('category'), pk=pk)

    return render(request, 'customers/postdetails.html', {'product': product})





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def con_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from content.models import Socails
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Socails, pk=pk)

        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:con_detail_d', pk=product.pk)
        else:
            form = PostForm(instance=product, tenant=tenant)

        return render(request, 'customers/postpdate.html', {'form': form, 'product': product})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_content(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:con_detail_d', pk=product.pk)
        else:
            form = PostForm(tenant=tenant)

        return render(request, 'customers/postcreate.html', {'form': form})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_con(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Socails, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_pcon')  
    

@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_camp(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Campagin

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Campagin.objects.select_related('social').all().order_by('-id'))

    return render(request, 'customers/postcon.html', {
        'tenant': tenant,
        'products': products,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def camp_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import Campagin
        product = get_object_or_404(Campagin.objects.select_related('social')
            .prefetch_related(
                'social__category',
            ), pk=pk)

    return render(request, 'customers/postdetailscam.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def camp_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from content.models import Campagin
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Campagin, pk=pk)

        if request.method == 'POST':
            form = CampForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:camp_detail_d', pk=product.pk)
        else:
            form = CampForm(instance=product, tenant=tenant)

        return render(request, 'customers/campuc.html', {'form': form, 'product': product})

@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_camp(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = CampForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:camp_detail_d', pk=product.pk)
        else:
            form = CampForm(tenant=tenant)

        return render(request, 'customers/campuc.html', {'form': form})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_camp(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Campagin, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_camp')  
    


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_Mess(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Campagin

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Mess.objects.all().order_by('-id'))

    return render(request, 'customers/postclient.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def mess_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import Mess
        product = get_object_or_404(Mess, pk=pk)

    return render(request, 'customers/postdetailmess.html', {'product': product})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_mess(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Mess, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Mess')  
    



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_service(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Campagin

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Service.objects.all().order_by('-id'))

    return render(request, 'customers/postservice.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def service_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import Service
        product = get_object_or_404(Service, pk=pk)

    return render(request, 'customers/postdetailserv.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def service_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from content.models import Service
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Service, pk=pk)

        if request.method == 'POST':
            form = ServiceForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:service_detail_d', pk=product.pk)
        else:
            form = ServiceForm(instance=product, tenant=tenant)

        return render(request, 'customers/servup.html', {'form': form, 'product': product})






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_services(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = ServiceForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:service_detail_d', pk=product.pk)
        else:
            form = ServiceForm(tenant=tenant)

        return render(request, 'customers/servup.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_service(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Service, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_service')  
    



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_company(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from company.models import Ideal

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Ideal.objects.all().order_by('-id'))

    return render(request, 'customers/company_ideal.html', {
        'tenant': tenant,
        'products': products,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_detail_company(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from company.models import Ideal
        product = get_object_or_404(Ideal, pk=pk)

    return render(request, 'customers/companyhd.html', {'product': product})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_edit_company(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from company.models import Ideal
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Ideal, pk=pk)

        if request.method == 'POST':
            form = HocompanyForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:home_detail_company', pk=product.pk)
        else:
            form = HocompanyForm(instance=product, tenant=tenant)

        return render(request, 'customers/comppp.html', {'form': form, 'product': product})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_company_service(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from company.models import Serv

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Serv.objects.all().order_by('-id'))

    return render(request, 'customers/company_serv.html', {
        'tenant': tenant,
        'products': products,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_detail_compser(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from company.models import Serv
        product = get_object_or_404(Serv, pk=pk)

    return render(request, 'customers/companysd.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_edit_compser(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from company.models import Serv
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Serv, pk=pk)

        if request.method == 'POST':
            form = SerompanyForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:home_detail_compser', pk=product.pk)
        else:
            form = SerompanyForm(instance=product, tenant=tenant)

        return render(request, 'customers/com_se.html', {'form': form, 'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_create_compser(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = SerompanyForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:home_detail_compser', pk=product.pk)
        else:
            form = SerompanyForm(tenant=tenant)

        return render(request, 'customers/com_se.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_servcom(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Serv, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_company_service')  
    



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_company_leader(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from company.models import Leaders

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Leaders.objects.all().order_by('-id'))

    return render(request, 'customers/company_lead.html', {
        'tenant': tenant,
        'products': products,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_detail_coml(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from company.models import Leaders
        product = get_object_or_404(Leaders, pk=pk)

    return render(request, 'customers/comlead.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_edit_ccoml(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from company.models import Leaders
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Leaders, pk=pk)

        if request.method == 'POST':
            form = LeadompanyForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:home_detail_coml', pk=product.pk)
        else:
            form = LeadompanyForm(instance=product, tenant=tenant)

        return render(request, 'customers/com_le.html', {'form': form, 'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_create_coml(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = LeadompanyForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:home_detail_coml', pk=product.pk)
        else:
            form = LeadompanyForm(tenant=tenant)

        return render(request, 'customers/com_le.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_coml(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Leaders, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_company_leader')  
    











@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_company_about(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from company.models import Abut

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Abut.objects.all().order_by('-id'))

    return render(request, 'customers/com_abut.html', {
        'tenant': tenant,
        'products': products,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_detail_company_about(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from company.models import Abut
        product = get_object_or_404(Abut, pk=pk)

    return render(request, 'customers/comad.html', {'product': product})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_edit_company_about(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from company.models import Abut
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Abut, pk=pk)

        if request.method == 'POST':
            form = AdompanyForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:home_detail_company_about', pk=product.pk)
        else:
            form = AdompanyForm(instance=product, tenant=tenant)

        return render(request, 'customers/comau.html', {'form': form, 'product': product})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_commpany_client(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from company.models import Imes

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Imes.objects.all().order_by('-id'))

    return render(request, 'customers/comcli.html', {
        'tenant': tenant,
        'products': products,
    })





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def book_detail_comapny(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from company.models import Imes
        product = get_object_or_404(Imes, pk=pk)

    return render(request, 'customers/comok.html', {'product': product})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_book(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Imes, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Book')  
    





















@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_conab(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Home

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Home.objects.all().order_by('-id'))

    return render(request, 'customers/postconab.html', {
        'tenant': tenant,
        'products': products,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import Home
        product = get_object_or_404(Home, pk=pk)

    return render(request, 'customers/postdetailhomev.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from content.models import Home
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Home, pk=pk)

        if request.method == 'POST':
            form = HomeconForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:home_detail_d', pk=product.pk)
        else:
            form = HomeconForm(instance=product, tenant=tenant)

        return render(request, 'customers/hup.html', {'form': form, 'product': product})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_conabou(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Campagin

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(About.objects.all().order_by('-id'))

    return render(request, 'customers/postconabou.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def about_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import About
        product = get_object_or_404(About, pk=pk)

    return render(request, 'customers/postdetailaboutv.html', {'product': product})


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def about_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from content.models import About
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(About, pk=pk)

        if request.method == 'POST':
            form = AboutconForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:about_detail_d', pk=product.pk)
        else:
            form = AboutconForm(instance=product, tenant=tenant)

        return render(request, 'customers/Aaup.html', {'form': form, 'product': product})






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_photo(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from content.models import Campagin

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Photo.objects.all().order_by('-id'))

    return render(request, 'customers/photocon.html', {
        'tenant': tenant,
        'products': products,
    })



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def photo_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from phot.models import Photo
        product = get_object_or_404(Photo, pk=pk)

    return render(request, 'customers/photodetailscam.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def photo_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from phot.models import Photo
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Photo, pk=pk)

        if request.method == 'POST':
            form = PhotoForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:photo_detail_d', pk=product.pk)
        else:
            form = PhotoForm(instance=product, tenant=tenant)

        return render(request, 'customers/photouc.html', {'form': form, 'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def photo_create_camp(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = PhotoForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:photo_detail_d', pk=product.pk)
        else:
            form = PhotoForm(tenant=tenant)

        return render(request, 'customers/photouc.html', {'form': form})





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_photo(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Photo, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_photo')  
    



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_serphot(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from phot.models import Service_Photo

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Service_Photo.objects.all().order_by('-id'))

    return render(request, 'customers/servcon.html', {
        'tenant': tenant,
        'products': products,
    })



@login_required
def pser_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from phot.models import Service_Photo
        product = get_object_or_404(Service_Photo, pk=pk)

    return render(request, 'customers/photoserv.html', {'product': product})





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def phserv_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from phot.models import Service_Photo
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Service_Photo, pk=pk)

        if request.method == 'POST':
            form = SerphotForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:pser_detail_d', pk=product.pk)
        else:
            form = SerphotForm(instance=product, tenant=tenant)

        return render(request, 'customers/servphoto.html', {'form': form, 'product': product})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def phser_create_camp(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = SerphotForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:pser_detail_d', pk=product.pk)
        else:
            form = SerphotForm(tenant=tenant)

        return render(request, 'customers/servphoto.html', {'form': form})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_phser(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Service_Photo, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_serphot')  
    





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_myself(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from phot.models import Myself

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Myself.objects.all().order_by('-id'))

    return render(request, 'customers/myself.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def aboutp_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from phot.models import Myself
        product = get_object_or_404(Myself, pk=pk)

    return render(request, 'customers/myselfdet.html', {'product': product})





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def phabout_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from phot.models import Myself
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Myself, pk=pk)

        if request.method == 'POST':
            form = ABouphotForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:aboutp_detail_d', pk=product.pk)
        else:
            form = ABouphotForm(instance=product, tenant=tenant)

        return render(request, 'customers/aboutbb.html', {'form': form, 'product': product})










@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_Book(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from phot.models import Bookings

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Bookings.objects.all().order_by('-id'))

    return render(request, 'customers/photoclient.html', {
        'tenant': tenant,
        'products': products,
    })





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def book_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from content.models import Mess
        product = get_object_or_404(Bookings, pk=pk)

    return render(request, 'customers/photobook.html', {'product': product})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_book(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Bookings, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Book')  
    












from django.http import JsonResponse

from django.utils import timezone
from calendar import monthrange
from datetime import datetime



def orders_chart_page(request):
    """
    Renders the page with Chart.js and UI controls.
    """
    return render(request, "customers/orders_chart.html", {
        "today": timezone.localdate(),
    })



from django.http import JsonResponse
from django.utils import timezone
from calendar import monthrange
from django_tenants.utils import schema_context

def orders_chart_data(request):
    tenant = request.user.tenant  # SAFE: just getting tenant object

    from ecom.models import Sale   # DO NOT load this inside schema_context

    # Parameters
    view = request.GET.get("view", "year")

    try:
        year = int(request.GET.get("year", timezone.now().year))
    except:
        year = timezone.now().year

    # ======================================
    #           MONTH VIEW
    # ======================================
    if view == "month":
        try:
            month = int(request.GET.get("month", timezone.now().month))
        except:
            month = timezone.now().month

        days = monthrange(year, month)[1]
        labels = [str(d) for d in range(1, days + 1)]
        totals = [0.0] * days

        # All DB queries MUST be inside schema_context
        with schema_context(tenant.schema_name):
            sales = Sale.objects.filter(
                created_at__year=year,
                created_at__month=month
            )

            for sale in sales:
                totals[sale.created_at.day - 1] += sale.total or 0

        return JsonResponse({
            "labels": labels,
            "data": totals,
            "view": "month",
            "year": year,
            "month": month,
        })

    # ======================================
    #           YEAR VIEW
    # ======================================
    labels = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
    totals = [0.0] * 12

    with schema_context(tenant.schema_name):
        sales = Sale.objects.filter(
            created_at__year=year
        )

        for sale in sales:
            totals[sale.created_at.month - 1] += sale.total or 0

    return JsonResponse({
        "labels": labels,
        "data": totals,
        "view": "year",
        "year": year,
    })








from django.core.paginator import Paginator
from django.utils import timezone
from django_tenants.utils import schema_context
from django.http import JsonResponse
from ecom.models import Sale

def sales_table_data(request):
    tenant = request.user.tenant
    view = request.GET.get("view", "year")
    try:
        year = int(request.GET.get("year", timezone.now().year))
    except:
        year = timezone.now().year
    page = int(request.GET.get("page", 1))
    month = request.GET.get("month")
    if month:
        month = int(month)

    with schema_context(tenant.schema_name):
        qs = Sale.objects.all()
        if view == "year":
            qs = qs.filter(created_at__year=year)
        elif view == "month" and month:
            qs = qs.filter(created_at__year=year, created_at__month=month)
        qs = qs.order_by("-created_at")  # Recent first

        paginator = Paginator(qs, 30)
        page_obj = paginator.get_page(page)

        rows = []
        for sale in page_obj.object_list:
            rows.append({
                "id": sale.id,
                "date": sale.created_at.strftime("%b %d, %Y"),
                "orders": sale.product.count(),
                "gross_sales": f"{sale.reference}",

                "net_sales": f"{sale.total:,.2f}",
            })

    return JsonResponse({
        "rows": rows,
        "total": paginator.count,
        "start": page_obj.start_index(),
        "end": page_obj.end_index(),
    })








@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def sales_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        sale = get_object_or_404(Sale, pk=pk)
        products = list(sale.product.all())  # get related products

    context = {
        'sale': sale,
        'products': products
    }
    return render(request, 'customers/sale_det.html', context)







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def sale_create(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = SaletForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:sales_detail_d', pk=product.pk)
        else:
            form = SaletForm(tenant=tenant)

        return render(request, 'customers/salec.html', {'form': form})





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def sale_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import Sale
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Sale, pk=pk)

        if request.method == 'POST':
            form = SaletForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:sales_detail_d', pk=product.pk)
        else:
            form = SaletForm(instance=product, tenant=tenant)

        return render(request, 'customers/salec.html', {'form': form, 'product': product})








@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_sale(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Sale, pk=pk)

        cat.delete()
    
    return redirect('customers:orders_chart_page')  
    

@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_comment(request, pk):
    tenant = request.user.tenant
    with schema_context(tenant.schema_name):
        from blog.models import Comm, Blog

        comment = get_object_or_404(Comm, id=pk)

        # Find the blog where this comment is attached
        blog = Blog.objects.filter(comment=comment).first()

        # Remove comment from blog comment list
        if blog:
            blog.comment.remove(comment)

        # Then delete it
        comment.delete()

    messages.success(request, "Comment deleted successfully.")
    return redirect('customers:home_detail_blog', pk=blog.id if blog else 1)








@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_Blog(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from blog.models import Blog

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Blog.objects.all().order_by('-id'))

    return render(request, 'customers/blogp.html', {
        'tenant': tenant,
        'products': products,
    })


@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_detail_blog(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from blog.models import Blog, Comm
        product = Blog.objects.prefetch_related(
            Prefetch("comment", queryset=Comm.objects.all())
        ).get(pk=pk)

    return render(request, 'customers/blogd.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_edit_blog(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from blog.models import Blog
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Blog, pk=pk)

        if request.method == 'POST':
            form = BlyForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:home_detail_blog', pk=product.pk)
        else:
            form = BlyForm(instance=product, tenant=tenant)

        return render(request, 'customers/blogf.html', {'form': form, 'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_create_blog(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = BlyForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:home_detail_blog', pk=product.pk)
        else:
            form = BlyForm(tenant=tenant)

        return render(request, 'customers/com_se.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_blog(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Blog, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Blog')  
    





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_Book_blog(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from blog.models import Msg

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Msg.objects.all().order_by('-id'))

    return render(request, 'customers/blogm.html', {
        'tenant': tenant,
        'products': products,
    })





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def book_detail_blog(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from blog.models import Msg
        product = get_object_or_404(Msg, pk=pk)

    return render(request, 'customers/blogb.html', {'product': product})







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_book_blog(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Msg, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Book_blog')  
    







@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_Book_blog_about(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from blog.models import Abbb

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Abbb.objects.all().order_by('-id'))

    return render(request, 'customers/blog_abut.html', {
        'tenant': tenant,
        'products': products,
    })





@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def book_detail_blog_about(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from blog.models import Abbb
        product = get_object_or_404(Abbb, pk=pk)

    return render(request, 'customers/bloa.html', {'product': product})




@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def home_about_blog(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from blog.models import Abbb
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Abbb, pk=pk)

        if request.method == 'POST':
            form = BAbuForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:book_detail_blog_about', pk=product.pk)
        else:
            form = BAbuForm(instance=product, tenant=tenant)

        return render(request, 'customers/bloaf.html', {'form': form, 'product': product})









@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_restaurant(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from restaurant.models import Menu

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Menu.objects.all().order_by('-id'))

    return render(request, 'customers/resss.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required 
def restaurant_detail_d(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from restaurant.models import Menu
        product = get_object_or_404(Menu.objects.select_related('category'), pk=pk)

    return render(request, 'customers/resd.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def restaurant_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from restaurant.models import Menu
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Menu, pk=pk)

        if request.method == 'POST':
            form = MenuForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:restaurant_detail_d', pk=product.pk)
        else:
            form = MenuForm(instance=product, tenant=tenant)

        return render(request, 'customers/ressup.html', {'form': form, 'product': product})






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_menu(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = MenuForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:restaurant_detail_d', pk=product.pk)
        else:
            form = MenuForm(tenant=tenant)

        return render(request, 'customers/ressup.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_menu(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Menu, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_restaurant')  
    









@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_restaurant_cat(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from restaurant.models import Catgg

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Catgg.objects.all().order_by('-id'))

    return render(request, 'customers/resc.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required 
def restaurant_detail_d_cat(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from restaurant.models import Catgg
        product = get_object_or_404(Catgg, pk=pk)

    return render(request, 'customers/rescd.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def restaurant_edit_d_cat(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from restaurant.models import Catgg
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Catgg, pk=pk)

        if request.method == 'POST':
            form = RcatForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:restaurant_detail_d_cat', pk=product.pk)
        else:
            form = RcatForm(instance=product, tenant=tenant)

        return render(request, 'customers/rescu.html', {'form': form, 'product': product})






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_create_restaurant_cat(request):
    tenant = request.user.tenant  # get current user's tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        if request.method == 'POST':
            form = RcatForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                product = form.save()
                return redirect('customers:restaurant_detail_d_cat', pk=product.pk)
        else:
            form = RcatForm(tenant=tenant)

        return render(request, 'customers/rescu.html', {'form': form})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_res_cat(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Catgg, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_restaurant_cat')  
    










@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_restaurant_home(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from restaurant.models import Hom

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Hom.objects.all().order_by('-id'))

    return render(request, 'customers/resh.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required 
def restaurant_detail_d_home(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from restaurant.models import Hom
        product = get_object_or_404(Hom, pk=pk)

    return render(request, 'customers/reshd.html', {'product': product})



@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def restaurant_edit_d_home(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from restaurant.models import Hom
    from django.shortcuts import get_object_or_404, redirect, render

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        product = get_object_or_404(Hom, pk=pk)

        if request.method == 'POST':
            form = HrForm(request.POST, request.FILES, instance=product, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:restaurant_detail_d_home', pk=product.pk)
        else:
            form = HrForm(instance=product, tenant=tenant)

        return render(request, 'customers/reshu.html', {'form': form, 'product': product})






@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_restaurant_Book(request):
    tenant = request.user.tenant  # tenant link
    products = []

    from restaurant.models import Bookdbdbd

    import cloudinary
    from django_tenants.utils import schema_context

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        products = list(Bookdbdbd.objects.all().order_by('-id'))

    return render(request, 'customers/resb.html', {
        'tenant': tenant,
        'products': products,
    })




@ratelimit(key='ip', rate='15/m', block=True)
@login_required 
def restaurant_detail_d_Book(request, pk):
    tenant = request.user.tenant

    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )
        from restaurant.models import Bookdbdbd
        product = get_object_or_404(Bookdbdbd, pk=pk)

    return render(request, 'customers/resbd.html', {'product': product})










@ratelimit(key='ip', rate='15/m', block=True)
@login_required
def dashboard_delete_res_book(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Bookdbdbd, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_restaurant_cat')  
    
































































































def authenticate_tenant(api_key):
    try:
        tenant_key = TenantAPIKey.objects.get(api_key=api_key)
        return tenant_key.tenant
    except TenantAPIKey.DoesNotExist:
        return None

# @csrf_exempt
# def api_add_product(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid method'}, status=405)

#     data = json.loads(request.body)
#     api_key = data.get('api_key')
#     tenant = authenticate_tenant(api_key)
#     if not tenant:
#         return JsonResponse({'error': 'Unauthorized'}, status=401)

#     with schema_context(tenant.schema_name):
#         product = Product.objects.create(
#             name=data['name'],
#             price=data['price'],
#             quantity=data.get('stock', 0),
#             description=data.get('description', ''),
#             discount_price=data.get('discount_price', 0),
#             size=data.get('size', ''),
#             color=data.get('color', ''),

#         )
#         return JsonResponse({'status': 'success', 'product_id': product.id})











@csrf_exempt
def whatsapp_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=405)

    data = request.POST.dict()

    print("Incoming Twilio Data →", data)
    incoming_msg = data.get('Body')
    from_number = data.get('From')
    


    tenant = Client.objects.filter(phone_number__icontains=from_number.replace('whatsapp:', '')).first()
    if not tenant:
        return JsonResponse({'error': 'Unauthorized number'}, status=401)

    with schema_context(tenant.schema_name):
        response_msg = handle_ai_command(incoming_msg, tenant)

    # Send reply through Twilio
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    payload = {
        'From': 'whatsapp:+14155238886',
        'To': from_number,
        'Body': response_msg
    }
    twilio_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
    requests.post(twilio_url, data=payload, auth=(account_sid, auth_token))
    r = requests.post(twilio_url, data=payload, auth=(account_sid, auth_token))
    print("Twilio SEND RESPONSE →", r.status_code, r.text)

    return JsonResponse({'status': 'success'})




openai_client = openai.OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are a product assistant for a store-management system.
You MUST respond ONLY in valid JSON. Never send text outside JSON.

Your output MUST follow exactly this structure:

{
  "action": "<add_product | check_product | create_sales | monthly_report | ask | chat>",
  "details": { ... }
}

--- INTENT RULES ---

1) ADD PRODUCT (user says: "add", "add product", "new product", "create product")
- Required fields: name, price, quantity
- If ANY missing -> return:
{
  "action": "ask",
  "details": {
    "missing": ["price", "quantity","name"],
    "message": "Please provide the missing information. let me know the product name, price and quantity "
  }
}

2) CHECK PRODUCT (user asks about availability or price)
Return:
{
  "action": "check_product",
  "details": {"name": "<product name>"}
}

3) CREATE SALES (user says: "add sale", "record sale", "sold", "sales")

- Required: name, quantity, price
- If missing → return action=ask
- Output:
{
  "action": "create_sales",
  "details": {
      "name": "...",
      "quantity": 2,
      "price": "200k"
  }
}

4) MONTHLY REPORT (user asks for report, stats, performance)
Return:
{
  "action": "monthly_report",
  "details": {}
}

5) NORMAL CHAT
Return:
{
  "action": "chat",
  "details": {"message": "<friendly reply>"}
}

You MUST ALWAYS output JSON only.
"""

@csrf_exempt
def handle_ai_command(message, tenant):
    from .models import ChatHistory
    import json

    # === Save incoming message ===
    ChatHistory.objects.create(
        tenant=tenant,
        user_number=tenant.phone_number,
        role="user",
        content=message
    )

    # === Get last 10 messages only ===
    recent_msgs = ChatHistory.objects.filter(
        tenant=tenant,
        user_number=tenant.phone_number
    ).order_by("-created_at")[:20]

    recent_msgs = reversed(recent_msgs)  # chronological order
    

    # === Build conversation ===
    ai_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in recent_msgs:
        ai_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    try:
        # === Call Groq ===
        response = openai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=ai_messages,
            temperature=0.2
        )

        ai_reply = response.choices[0].message.content.strip()

        print("\n================ RAW AI REPLY ================")
        print(ai_reply)
        print("==============================================\n")

        # === Parse JSON ===
        try:
            reply_json = json.loads(ai_reply)
        except json.JSONDecodeError:
            print("JSON decode error!")
            fallback_msg = "Please reply again in simple words."
            ChatHistory.objects.create(
                tenant=tenant, user_number=tenant.phone_number,
                role="assistant", content=fallback_msg
            )
            return fallback_msg

        action = reply_json.get("action")
        details = reply_json.get("details", {})

        # === EXECUTE ACTION ===
        if action == "add_product":
            response_text = api_add_product_internal(details, tenant)
        elif action == "check_product":
            response_text = check_product_internal(details, tenant)
        elif action == "create_sales":
            response_text = create_sales_internal(details, tenant)
        elif action == "monthly_report":
            response_text = monthly_report_internal(tenant)
        elif action == "ask":
            # AI is asking user for missing fields
            response_text = details.get("message", "Provide missing fields.")
        elif action == "chat":
            response_text = details.get("message", "Hello!")

        else:
            # Should never happen unless AI breaks
            response_text = "I could not recognize the action. Please try again."

        # === Save AI reply ===
        ChatHistory.objects.create(
            tenant=tenant,
            user_number=tenant.phone_number,
            role="assistant",
            content=response_text
        )

        return response_text

    except Exception as e:
        print("Groq AI error:", e)
        return "AI service unavailable. Please try again later."
# === Internal Functions ===
import re

def clean_price(value):
    """
    Cleans AI price values like:
    - "200,000"
    - "200000"
    - "200,000 naira"
    - "₦200,000"
    - "200k"
    - "200k naira"

    Returns integer price, or None if invalid.
    """

    if value is None:
        return None

    value = str(value).lower().strip()

    # Replace commas, currency symbols, and words
    value = value.replace(",", "")
    value = value.replace("₦", "")
    value = value.replace("ngn", "")
    value = value.replace("naira", "")
    value = value.replace("n", "")

    # Convert "200k" → 200000
    if value.endswith("k"):
        try:
            num = float(value[:-1]) * 1000
            return int(num)
        except:
            pass

    # Extract digits
    match = re.findall(r"\d+", value)
    if match:
        return int(match[0])

    return None








def api_add_product_internal(data, tenant):
    from ecom.models import Product

    # Clean & validate
    name = data.get("name")
    price = clean_price(data.get("price"))
    quantity = data.get("quantity")

    if not name or price is None or quantity is None:
        return "❌ Missing fields. Please provide name, price, and quantity."

    with schema_context(tenant.schema_name):
        product = Product.objects.create(
            name=name,
            price=price,
            quantity=quantity,
            description=data.get("description", ""),
            discount_price=clean_price(data.get("discount_price")),
            size=data.get("size", ""),
            color=data.get("color", "")
        )
        return f"✅ Product '{product.name}' added successfully at ₦{price:,}!"





def check_product_internal(data, tenant):
    from ecom.models import Product
    with schema_context(tenant.schema_name):
        product = Product.objects.filter(name__icontains=data.get("name")).first()
        if product:
            return f"🛒 '{product.name}' is available at ₦{product.price} and quantity of {product.quantity}."
        return "❌ Product not found."





def create_sales_internal(data, tenant):
    from ecom.models import Product, Sale

    name = data.get("name")
    quantity = data.get("quantity")
    total = clean_price(data.get("price"))

    if not name:
        return "❌ Please provide the product name."

    with schema_context(tenant.schema_name):

        # 🔍 FIND MATCHING PRODUCT(S)
        products = Product.objects.filter(name__icontains=name)

        if not products.exists():
            return f"❌ Product '{name}' not found. Should I create it?"

        # Multiple similar products
        if products.count() > 1:
            product_names = ", ".join([p.name for p in products])
            return f"⚠️ Multiple products found: {product_names}. Which one was sold?"

        # Exactly 1 match → ask for confirmation
        product = products.first()

        # Build confirmation message
        confirm_msg = (
            f"❓ Is this the *{product.name}* that has *{product.quantity}* quantity "
            f"and price is *₦{product.price:,}* that you sold?\n\n"
            f"👉 How many quantity did you sell?"
        )

        # Store pending confirmation
        set_pending_action(tenant, {
            "type": "confirm_product_for_sale",
            "product_id": product.id,
            "total": total,       # May be None if user didn’t specify yet
            "quantity": quantity  # May be None (bot will ask again)
        })

        return confirm_msg








def monthly_report_internal(tenant):
    return "📊 Total sales last month: ₦500,000."


