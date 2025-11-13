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




from ecom.models import *





from functools import wraps
from b_manager.models import Client

from django_ratelimit.decorators import ratelimit


def tenant_ip_key(group, request):
    tenant = getattr(request, 'tenant', None)
    tenant_id = getattr(tenant, 'schema_name', 'public')
    ip = request.META.get('REMOTE_ADDR', '')
    return f"{tenant_id}:{ip}"







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

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key='ip', rate='40/m', block=True)
def plan_list(request):
    plans = SubscriptionPlan.objects.all().order_by('price')
    return render(request, 'customers/pricing.html', {'plans': plans})

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def job_list(request):
    client = Client.objects.filter(name=request.user.username).first()
    if not client or client.plan is None:
        messages.warning(request, "Please log in and choose a plan")
        return redirect('customers:plan_list')

    if client.job_type is not None:
        messages.warning(request, "Youve chosen a job type")
        return redirect('customers:web_sel')

    jobs = Job.objects.all().order_by('name')
    return render(request, 'customers/jobsel.html', {'jobs': jobs})




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def upgrade_init(request):
    if request.method != 'POST':
        return redirect('customers:plan_list')
    
    plan_id = request.POST.get('plan_id')
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    payer_email = request.user.email if request.user.is_authenticated else request.POST.get('email')

    if not payer_email:
        return redirect('customers:plan_list')

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

        # ✅ Always update the plan to "Free"
        tenant.plan = plan
        tenant.trial_ends_on = None
        tenant.paid_until = None
        tenant.is_active = True
        tenant.save()

        # Domain.objects.get_or_create(
        #     domain=f"{schema_name}.baxting.com",
        #     tenant=tenant,
        #     is_primary=True
        # )

        return render(request, 'customers/tksub.html', {
                'message': 'Free plan activated successfully!',
                'plan': plan
            })
    # 🔵 Basic Plan (7-day free trial)
    elif plan.name == 'Basic':
        tenant = create_trial_tenant(request, plan)
        if not tenant:
            paystack_plan_code = plan.plan_code

            metadata = {
                'tenant': getattr(request, 'tenant', None).schema_name if hasattr(request, 'tenant') else request.user.username.lower(),
                'plan_name': plan.name,
            }

            payload = {
                'email': payer_email,
                'amount': int(plan.price * 100),
                'plan': paystack_plan_code,
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

    # 🔴 Premium Plan (paid only — go through Paystack)
    else:
        paystack_plan_code = plan.plan_code

        metadata = {
            'tenant': getattr(request, 'tenant', None).schema_name if hasattr(request, 'tenant') else request.user.username.lower(),
            'plan_name': plan.name,
        }

        payload = {
            'email': payer_email,
            'amount': int(plan.price * 100),
            'plan': paystack_plan_code,
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
def paystack_verify(request):
    reference = request.GET.get('reference')
    if not reference:
        return render(request, 'customers/tksub.html', {'error': 'Missing transaction reference'})

    headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
    verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
    resp = requests.get(verify_url, headers=headers)
    data = resp.json()

    if data.get('status') and data['data']['status'] == 'success':
        metadata = data['data'].get('metadata', {})
        plan_name = metadata.get('plan_name')
        tenant_name = metadata.get('tenant')

        plan = SubscriptionPlan.objects.filter(name=plan_name).first()
        if plan:
            tenant = Client.objects.filter(schema_name=tenant_name).first()
            if tenant:
                tenant.plan = plan
                tenant.paid_until = timezone.now() + timedelta(days=plan.duration_days)
                tenant.save()

            schema_name = request.user.username.lower()
              # or tenant_name if you stored it in metadata

            trial_end_date = date.today() + timedelta(days=30)


            tenant, created = Client.objects.get_or_create(
            schema_name=schema_name,
                defaults={
                    'name': request.user.username,
                    'email': request.user.email,
                    'is_active': True,
                    'trial_ends_on': trial_end_date,
                    'has_used_trial': True,
                    'plan': plan,
                }
            )
            request.user.tenant = tenant
            request.user.save()

            # Domain.objects.get_or_create(
            #     domain=f"{schema_name}.baxting.com",
            #     tenant=tenant,
            #     is_primary=True
            # )

            return render(request, 'customers/tksub.html', {
                'message': f'Payment successful! {plan.name} plan activated for {tenant.name}.',
                'plan': plan
            })

        return render(request, 'customers/tksub.html', {'message': 'Payment successful! Plan activated.'})

    return render(request, 'customers/tksub.html', {'error': 'Payment verification failed.'})





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def web_temp_detail(request, slug):

    webs = get_object_or_404(WebsiteTemplate, slug=slug)

    return render(request, 'customers/templatepreview.html', {'webs': webs})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)    
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









@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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

            messages.success(request, f"Your business details have been saved successfully! Domain: {domain_name}")
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




@ratelimit(key='ip', rate='30/m', block=True)
def about(request):

    return render(request, 'customers/about.html', {})



@ratelimit(key='ip', rate='30/m', block=True)
def help(request):
    return render(request, 'customers/help.html', {})




@ratelimit(key='ip', rate='30/m', block=True)
def terms(request):
    return render(request, 'customers/tems.html', {})


@ratelimit(key='ip', rate='30/m', block=True)
def privacy(request):
    return render(request, 'customers/privacyr.html', {})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
def switch(request):
    client = Client.objects.filter(name=request.user.username).first()

    if not client or client.plan is None:
        messages.warning(request, "Please log in and choose a plan")
        
        return redirect('customers:plan_list')
    subscription = client.plan

    return render(request, 'customers/subb.html', {'subscription':subscription})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def cancel_subscription(request):
    client = Client.objects.filter(name=request.user.username).first()

    if not client or client.plan is None:
        messages.warning(request, "You are not subscribed to any plan.")
        return redirect('customers:switch')

    if request.method == 'POST':

        client = Client.objects.filter(name=request.user.username).first()
        client.plan = None
        client.save(update_fields=['plan', 'paid_until', 'trial_ends_on', 'is_active'])

        messages.success(request, "Your subscription has been cancelled successfully.")
        return redirect('customers:plan_list')

    # Optional safety redirect if someone hits GET directly
    return redirect('customers:switch')



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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







@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
def verify_bank_account(request):
    bank_code = request.GET.get('bank')
    account_number = request.GET.get('account_no')

    if not bank_code or not account_number:
        return JsonResponse({'status': 'error', 'message': 'Missing bank or account number'})

    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)
    

    if data.get('status'):
        return JsonResponse({
            'status': 'success',
            'account_name': data['data']['account_name']
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid details'})












@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@onboarding_required
@login_required
def dashboard(request):
    client = get_object_or_404(Client, name=request.user.username)

  
        



    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        messages.info(request, "Please select a plan to activate your account.")
        return redirect('customers:plan_list')




    if client.plan is None:
        return redirect('customers:plan_list')
    if not client.job_type or client.job_type.name is None:
        return redirect('customers:job_list')
    if not client.template_type or client.template_type.name is None:
        return redirect('customers:web_sel')
    if not client.business_name or client.business_name is None:
        return redirect('customers:formad')
    if client.live is False:
        return redirect('customers:myweb')

 
    job_name = client.job_type.name if client.job_type else None
    if job_name == 'Store':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from ecom.models import Product, Order
            products = list(Product.objects.all())
            order = list(Order.objects.select_related('address').filter(Paid=True).all())
        return render(request, 'customers/dashboard.html',{'products':products,'order':order, 'client':client})
    if job_name == 'Influencers':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from content.models import Mess
            products = list(Mess.objects.all())
        return render(request, 'customers/dashboard_content.html',{'products':products, 'client':client})
    if job_name == 'Photo Artist':

        tenant = request.user.tenant 
        products = []

       
        with schema_context(tenant.schema_name):
            from phot.models import Bookings
            products = list(Bookings.objects.all())
        return render(request, 'customers/dashboard_photo.html',{'products':products, 'client':client})
    else:
        return redirect('customers:plan_list')



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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






# for ManyToManyField
# @login_required
# def product_detail_d(request, pk):
#     tenant = request.user.tenant

#     with schema_context(tenant.schema_name):
#         from ecommerce.models import Product  # ✅ import inside context
#         product = get_object_or_404(Product.objects.prefetch_related('category'), pk=pk)



#     return render(request, 'customers/productdetails.html', {'product': product})










@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
# @login_required
# def dashboard_products(request):
#     tenant = getattr(request.user, 'tenant', None)

#     if not tenant:
#         return redirect('customers:plan_list')

#     with schema_context(tenant.schema_name):
#         from dashboard.models import Product
#         products = Product.objects.all()

#     return render(request, 'dashboard/products.html', {'products': products})

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
def delete_p(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, pk=pk)

    return render(request, 'customers/del_p.html',{'product':product})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
@require_POST
def mark_order_delivered(request, order_id):
    tenant = request.user.tenant
    with schema_context(tenant.schema_name):
        from ecom.models import Order
        order = get_object_or_404(Order, pk=order_id)
        if order.status == 'shipping':
            order.status = 'delivered'
            order.save()
        else:
            order.status = 'delivered'
            order.save()
    return redirect('customers:order_detail_d', pk=order_id)



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def order_detail_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import Order

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

    return render(request, 'customers/Orderdedt.html', {'order': order})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_order(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        order = get_object_or_404(Order, pk=pk)

        order.delete()
    
    return redirect('customers:dashboard_orderlist')  
    



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def coupon_detail_d(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import Coupon  # ✅ import inside context
        coupon = get_object_or_404(Coupon, pk=pk)

    return render(request, 'customers/coupondet.html', {'coupon': coupon})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_coupon(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        coupon = get_object_or_404(Coupon, pk=pk)

        coupon.delete()
    
    return redirect('customers:dashboard_couponlist')  
    


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def category_detail_d(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import Category  # ✅ import inside context
        category = get_object_or_404(Category, pk=pk)

    return render(request, 'customers/catrgoryd.html', {'category': category})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_cat(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Category, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_catlist')  
    




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_del(request):
    tenant = request.user.tenant

    
    return render(request,'customers/Delivery.html',{})  
    


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def delivery_detail_d(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import DeliveryState  # ✅ import inside context
        category = get_object_or_404(DeliveryState, pk=pk)

    return render(request, 'customers/deliveryd.html', {'category': category})



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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







@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_del(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(DeliveryState, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_del_other')  
    




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_del_lag(request):
    tenant = request.user.tenant

    # Fetch & evaluate inside schema context
    with schema_context(tenant.schema_name):
        delivery = list(DeliveryCity.objects.select_related('state'))

    return render(request, 'customers/lagl.html', {
        'tenant': tenant,
        'delivery': delivery,
    })


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def delivery_detail_lag(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        from ecom.models import DeliveryCity  # ✅ import inside context
        category = get_object_or_404(DeliveryCity, pk=pk)

    return render(request, 'customers/lagd.html', {'category': category})


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def lag_edit_d(request, pk):
    tenant = request.user.tenant

    from django_tenants.utils import schema_context
    from ecom.models import DeliveryCity
    from django.shortcuts import get_object_or_404, redirect, render

    with schema_context(tenant.schema_name):
        category = get_object_or_404(DeliveryCity, pk=pk)

        if request.method == 'POST':
            form = DelCityForm(request.POST, request.FILES, instance=category, tenant=tenant)
            if form.is_valid():
                form.save()
                return redirect('customers:delivery_detail_lag', pk=category.pk)
        else:
            form = DelCityForm(instance=category, tenant=tenant)

        return render(request, 'customers/lagu.html', {'form': form, 'category': category})

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_create_lag(request):
    tenant = request.user.tenant  # get current user's tenant

    with schema_context(tenant.schema_name):
        if request.method == 'POST':
            form = DelCityForm(request.POST, request.FILES, tenant=tenant)
            if form.is_valid():
                category = form.save()
                return redirect('customers:delivery_detail_lag', pk=category.pk)
        else:
            form = DelCityForm(tenant=tenant)

        return render(request, 'customers/lagc.html', {'form': form})



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_lag(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(DeliveryCity, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_del_lag')  
    






@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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







@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_con(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Socails, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_pcon')  
    

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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

@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_camp(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Campagin, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_camp')  
    


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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







@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_mess(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Mess, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Mess')  
    



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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






@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_service(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Service, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_service')  
    


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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


@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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






@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_photo(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Photo, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_photo')  
    



@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_phser(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Service_Photo, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_serphot')  
    





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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




@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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










@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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





@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
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







@ratelimit(key=tenant_ip_key, rate='40/m', block=True)
@login_required
def dashboard_delete_book(request, pk):
    tenant = request.user.tenant

    with schema_context(tenant.schema_name):
        cat = get_object_or_404(Bookings, pk=pk)

        cat.delete()
    
    return redirect('customers:dashboard_Book')  
    









































































































































def authenticate_tenant(api_key):
    try:
        tenant_key = TenantAPIKey.objects.get(api_key=api_key)
        return tenant_key.tenant
    except TenantAPIKey.DoesNotExist:
        return None

@csrf_exempt
def api_add_product(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    data = json.loads(request.body)
    api_key = data.get('api_key')
    tenant = authenticate_tenant(api_key)
    if not tenant:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    with schema_context(tenant.schema_name):
        product = Product.objects.create(
            name=data['name'],
            price=data['price'],
            quantity=data.get('stock', 0),
            description=data.get('description', ''),
            discount_price=data.get('discount_price', 0),
            size=data.get('size', ''),
            color=data.get('color', ''),

        )
        return JsonResponse({'status': 'success', 'product_id': product.id})











@csrf_exempt
def whatsapp_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=405)

    data = request.POST or json.loads(request.body.decode('utf-8'))
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

    return JsonResponse({'status': 'success'})





def handle_ai_command(message, tenant):
    GROQ_API_KEY = "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"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an intelligent business assistant that helps users manage their shop. "
                    "If the user's message is a command (like add product, create order, check stock, or sales report), "
                    "return conversation explain how they should send their product details"
                    "If it's casual chat (like 'hi', 'how are you', or 'what can you do'), "
                    "respond naturally in plain text — not JSON. but after greetings say you can't have casual conversations thats is not ralating to their shop"
                ),
            },
            {
                "role": "user",
                "content": f"Tenant: {tenant.name} | Schema: {tenant.schema_name} | Message: {message}",
            },
        ],
        "temperature": 0.4,
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        ai_reply = result["choices"][0]["message"]["content"].strip()

        # If it looks like JSON (for command mode)
        if ai_reply.startswith("{") and ai_reply.endswith("}"):
            try:
                parsed = json.loads(ai_reply)
                action = parsed.get("action")
                details = parsed.get("details", {})

                if action == "add_product":
                    return api_add_product_internal(details, tenant)
                elif action == "check_product":
                    return check_product_internal(details, tenant)
                elif action == "create_order":
                    return create_order_internal(details, tenant)
                elif action == "monthly_report":
                    return monthly_report_internal(tenant)
                else:
                    return "I couldn’t identify that action. Can you rephrase?"
            except json.JSONDecodeError:
                return "Sorry, I couldn’t process that command. Please rephrase."

        # Otherwise, just chat normally
        return ai_reply

    except requests.exceptions.RequestException as e:
        print("Groq API error:", e)
        return "AI service unavailable. Please try again later."


# === Internal Functions ===

def api_add_product_internal(data, tenant):
    with schema_context(tenant.schema_name):
        product = Product.objects.create(
            name=data.get("name"),
            price=data.get("price", 0),
            quantity=data.get("quantity", 0),
            description=data.get("description", ""),
            discount_price=data.get("discount_price", 0),
            size=data.get("size", ""),
            color=data.get("color", "")
        )
        return f"✅ Product '{product.name}' added successfully!"

def check_product_internal(data, tenant):
    with schema_context(tenant.schema_name):
        product = Product.objects.filter(name__icontains=data.get("name")).first()
        if product:
            return f"🛒 '{product.name}' is available at ₦{product.price}."
        return "❌ Product not found."

def create_order_internal(data, tenant):
    return "🧾 Order created successfully."

def monthly_report_internal(tenant):
    return "📊 Total sales last month: ₦500,000."


def api_add_product_internal(data, tenant):
    with schema_context(tenant.schema_name):
        product = Product.objects.create(
            name=data.get("name"),
            price=data.get("price", 0),
            quantity=data.get("quantity", 0),
            description=data.get("description", ""),
            discount_price=data.get("discount_price", 0),
            size=data.get("size", ""),
            color=data.get("color", "")
        )
        return f"✅ Product '{product.name}' added successfully!"

def check_product_internal(data, tenant):
    with schema_context(tenant.schema_name):
        product = Product.objects.filter(name__icontains=data.get("name")).first()
        if product:
            return f"🛒 '{product.name}' is available at ₦{product.price}."
        return "❌ Product not found."

def create_order_internal(data, tenant):
    # Placeholder for your order creation logic
    return "🧾 Order created successfully."

def monthly_report_internal(tenant):
    # Placeholder for monthly sales summary
    return "📊 Total sales last month: ₦500,000."
