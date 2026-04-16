from decimal import Decimal

import json
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_tenants.utils import schema_context

from django.core.mail import send_mail
# Create your views here.
from django.shortcuts import render, get_object_or_404,redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import random
import string


import requests
import json
import time
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse 
from django_ratelimit.decorators import ratelimit

from b_manager.models import WebsiteVisit,Client





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



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
    if request.user.is_authenticated:
        already_logged = WebsiteVisitgrtghbr.objects.filter(user=request.user).exists()
    else:
        already_logged = WebsiteVisitgrtghbr.objects.filter(ip_address=ip_address).exists()

    if already_logged:
        return JsonResponse({"status": "success", "message": "Visit already recorded recently"})

    # Save visit
    WebsiteVisitgrtghbr.objects.create(
        user=request.user if request.user.is_authenticated else None,
        path=data.get("path", "/"),
        referrer=data.get("referrer", ""),
        user_agent=data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
        ip_address=ip_address,
    )

    return JsonResponse({"status": "success"})


# from django_tenants.utils import get_tenant_model

# tenant = request.tenant  # This works if django-tenants is set up
# subaccount_id = tenant.flw_subaccount_id

# def get_delivery_distance(origin, destination):
#     api_key = settings.GOOGLE_API_KEY
    
#     url = (
#         f"https://maps.googleapis.com/maps/api/distancematrix/json?"
#         f"origins={origin}&destinations={destination}&key={api_key}"
#     )
    
#     response = requests.get(url).json()
#     print(response)

#     element = response['rows'][0]['elements'][0]

#     distance_km = element['distance']['value'] / 1000      # → KM
#     duration_min = element['duration']['value'] / 60       # → Minutes


#     return distance_km, duration_min

from urllib.parse import quote

def get_delivery_distance(origin, destination):
    api_key = settings.GOOGLE_API_KEY
    
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={quote(origin)}&destinations={quote(destination)}"
        f"&region=ng&key={api_key}"
    )
    
    response = requests.get(url).json()
    print(response)

    if response.get('status') != 'OK':
        print(f"Distance Matrix API error: {response.get('status')}")
        return None

    element = response['rows'][0]['elements'][0]

    if element.get('status') != 'OK':
        print(f"Element status: {element.get('status')} | origin={origin} | dest={destination}")
        return None

    distance_km = element['distance']['value'] / 1000
    duration_min = element['duration']['value'] / 60

    return distance_km, duration_min



@ratelimit(key='ip', rate='10/m', block=True)
def removecoupon(request):
    from ecom.models import Coupon, Category, Product, Cart, Address, DeliveryBase, DeliveryState, DeliveryCity, Order, Sale, Trans

    tenant = request.tenant
    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )

        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, Paid=False).last()
        else:
            order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

        if order and order.coupon:
            order.coupon = None
            order.save()
            messages.success(request, "Promo code removed successfully.")
        else:
            messages.info(request, "No promo code was applied.")

    return redirect('cart_view')




def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))




@ratelimit(key='ip', rate='10/m', block=True)
def get_coupon(request, code):
    from ecom.models import Coupon, Category, Product, Cart, Address, DeliveryBase, DeliveryState, DeliveryCity, Order, Sale, Trans

    tenant = request.tenant
    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )

        try:
            return Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return None


@ratelimit(key='ip', rate='10/m', block=True)
def home(request):
    from ecom.models import Coupon, Category, Product, Cart, Address, DeliveryBase, DeliveryState, DeliveryCity, Order, Sale, Trans

    tenant = request.tenant
    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )

        product_list = Product.objects.filter(image__isnull=False).order_by('-id')
        paginator = Paginator(product_list, 12)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

    return render(request, 'whiteecom/shop/home.html', {'products': products})

@ratelimit(key='ip', rate='10/m', block=True)
def product_list(request):
    from ecom.models import Coupon, Category, Product, Cart, Address, DeliveryBase, DeliveryState, DeliveryCity, Order, Sale, Trans

    tenant = request.tenant
    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )

        product_list = Product.objects.filter(best_sellers=True, image__isnull=False).order_by('-id')
        paginator = Paginator(product_list, 12)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

    return render(request, 'whiteecom/shop/shop.html', {'products': products})



@ratelimit(key='ip', rate='10/m', block=True)
def product_detail(request, slug):
    from ecom.models import Coupon, Category, Product, Cart, Address, DeliveryBase, DeliveryState, DeliveryCity, Order, Sale, Trans

    tenant = request.tenant
    import cloudinary

    with schema_context(tenant.schema_name):
        cloudinary.config(
            cloud_name=tenant.cloud_name,
            api_key=tenant.api_key,
            api_secret=tenant.api_secret,
        )

        product = get_object_or_404(Product, slug=slug)
        category = product.category
        related_products = (
            Product.objects.filter(category=category, image__isnull=False)
            .exclude(id=product.id)
            .order_by('-created_at')[:4]
        )

    return render(request, 'whiteecom/shop/productdet.html', {
        'product': product,
        'dud': related_products,
    })

@ratelimit(key='ip', rate='10/m', block=True)
def remove_from(request, slug):
    from ecom.models import Cart, Product

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, slug=slug)

        if request.user.is_authenticated:
            cart_item = (
                Cart.objects
                .filter(product=product, user=request.user, ordered=False)
                .first()
            )
        else:
            if not request.session.session_key:
                request.session.create()          # creates & saves the session
            session_key = request.session.session_key
            cart_item = (
                Cart.objects
                .filter(product=product, session_key=session_key, ordered=False)
                .first()
            )

        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")

    return redirect('productdet', slug=slug)





@ratelimit(key='ip', rate='10/m', block=True)
def cart_view(request):
    from ecom.models import Cart, Order

    tenant = request.tenant

    with schema_context(tenant.schema_name):

        # Resolve session key once, safely
        if not request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

        # Single cart fetch, ordered correctly
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(
                user=request.user, ordered=False
            ).order_by('-id').select_related('product')
        else:
            cart_items = Cart.objects.filter(
                session_key=session_key, ordered=False
            ).order_by('-id').select_related('product')

        # Evaluate once to avoid repeated queries
        cart_items = list(cart_items)

        # Fetch unpaid order
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, Paid=False).last()
        else:
            order = Order.objects.filter(session_key=session_key, Paid=False).last()

        # Calculate totals once
        subtotal = sum(item.get_final_price() for item in cart_items)

        coupon_amount = None
        if order and order.coupon:
            coupon_amount = order.coupon.amount
            discounted_total = max(subtotal - coupon_amount, 0)
        else:
            discounted_total = subtotal

    return render(request, 'whiteecom/shop/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'coupon_amount': coupon_amount,
        'total': discounted_total,
    })





@ratelimit(key='ip', rate='10/m', block=True)
def add_to(request, slug):
    from ecom.models import Cart, Product

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, slug=slug)

        if product.quantity <= 0:
            messages.warning(request, f"Sorry, {product.name} is out of stock.")
            return redirect('productdet', slug=slug)

        # Resolve identity once
        if request.user.is_authenticated:
            cart_filter = {'user': request.user, 'ordered': False, 'product': product}
            create_kwargs = {'user': request.user, 'session_key': None}
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart_filter = {'session_key': session_key, 'ordered': False, 'product': product}
            create_kwargs = {'user': None, 'session_key': session_key}

        # Lock the row to prevent race conditions on quantity
        cart_item = Cart.objects.select_for_update().filter(**cart_filter).first()

        if cart_item:
            if cart_item.quantity >= product.quantity:
                messages.warning(
                    request,
                    f"Only {product.quantity} of {product.name} left in stock."
                )
                return redirect('cart_view')

            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in your cart.")

        else:
            Cart.objects.create(
                product=product,
                ordered=False,
                quantity=1,
                **create_kwargs        # cleanly sets user/session_key, never both
            )
            messages.success(request, f"{product.name} added to your cart.")

    return redirect('cart_view')





@ratelimit(key='ip', rate='10/m', block=True)
def remove(request, slug):
    from ecom.models import Cart, Product

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, slug=slug)

        # Resolve identity once
        if request.user.is_authenticated:
            cart_filter = {'user': request.user, 'ordered': False, 'product': product}
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart_filter = {'session_key': session_key, 'ordered': False, 'product': product}

        cart_item = Cart.objects.filter(**cart_filter).first()

        if cart_item:
            if cart_item.quantity <= 1:
                cart_item.delete()
                messages.success(request, f"{product.name} removed from your cart.")
            else:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, f"{product.name} quantity reduced.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")

    return redirect('cart_view')


@ratelimit(key='ip', rate='10/m', block=True)
def remove_item(request, slug):
    from ecom.models import Cart, Product

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        product = get_object_or_404(Product, slug=slug)

        # Resolve identity once
        if request.user.is_authenticated:
            cart_filter = {'user': request.user, 'ordered': False, 'product': product}
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart_filter = {'session_key': session_key, 'ordered': False, 'product': product}

        # Shared delete logic — no duplication
        cart_item = Cart.objects.filter(**cart_filter).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")

    return redirect('cart_view')






@ratelimit(key='ip', rate='10/m', block=True)
def remove_all(request):
    from ecom.models import Cart

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        if request.user.is_authenticated:
            deleted_count, _ = Cart.objects.filter(
                user=request.user, ordered=False
            ).delete()
        else:
            session_key = request.session.session_key
            if session_key:
                deleted_count, _ = Cart.objects.filter(
                    session_key=session_key, ordered=False
                ).delete()
            else:
                deleted_count = 0

        if deleted_count:
            messages.success(request, "All items removed from your cart.")
        else:
            messages.warning(request, "Your cart is already empty.")

    return redirect('cart_view')









@ratelimit(key='ip', rate='10/m', block=True)
def checkout(request):
    from ecom.models import Cart, Order, Address, DeliveryBase, DeliveryState

    tenant = request.tenant

    with schema_context(tenant.schema_name):

        # Resolve session key once
        if not request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

        # Shared identity filter helpers
        def cart_filter():
            if request.user.is_authenticated:
                return Cart.objects.filter(user=request.user, ordered=False)
            return Cart.objects.filter(session_key=session_key, ordered=False)

        def order_filter():
            if request.user.is_authenticated:
                return Order.objects.filter(user=request.user, Paid=False).last()
            return Order.objects.filter(session_key=session_key, Paid=False).last()

        # Guard: empty cart
        cart_items = list(cart_filter().select_related('product'))
        if not cart_items:
            return redirect('cart_view')

        order = order_filter()

        # Calculate totals once
        subtotal = sum(item.get_final_price() for item in cart_items)
        coupon_amount = None
        if order and order.coupon:
            coupon_amount = order.coupon.amount
            if subtotal <= coupon_amount:
                messages.error(request, "Your coupon value meets or exceeds your cart total.")
                return redirect('cart_view')
            discounted_total = subtotal - coupon_amount
        else:
            discounted_total = subtotal

        # Default address for GET display
        if request.user.is_authenticated:
            default_address_s = Address.objects.filter(
                user=request.user, default=True
            ).first()
        else:
            default_address_s = Address.objects.filter(
                session_key=session_key, default=True
            ).first()

        if request.method == 'POST':
            use_default = request.POST.get('use_default') == 'on'
            save_address = request.POST.get('save_address') == 'on'

            # Resolve address
            if use_default and request.user.is_authenticated:
                if not default_address_s:
                    messages.warning(request, "You don't have a default address yet.")
                    return redirect('checkout')
                address = default_address_s
            else:
                # Collect and create new address from form
                first_name   = request.POST.get('first_name')
                last_name    = request.POST.get('last_name')
                email        = request.POST.get('email')
                street_address = request.POST.get('street_address')
                apartment    = request.POST.get('apartment')
                city         = request.POST.get('city')
                state        = request.POST.get('state')
                country      = request.POST.get('country')
                phone_number = request.POST.get('phone_number')

                address = Address.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=None if request.user.is_authenticated else session_key,
                    first_name=first_name,
                    last_name=last_name,
                    email=request.user.email if request.user.is_authenticated else email,
                    street_address=street_address,
                    apartment=apartment,
                    city=city,
                    state=state,
                    country=country,
                    phone_number=phone_number,
                    default=False,
                )

                if save_address and request.user.is_authenticated:
                    Address.objects.filter(user=request.user, default=True).update(default=False)
                    address.default = True
                    address.save()
                    messages.success(request, "Address saved as your default.")

            # Create or update order
            order_email = request.user.email if request.user.is_authenticated else request.POST.get('email', '')
            if order:
                order.address = address
                order.email = order_email
                order.ref_code = create_ref_code()
                order.ordered_date = timezone.now()
                order.amount = discounted_total
                order.save()
            else:
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=None if request.user.is_authenticated else session_key,
                    Paid=False,
                    address=address,
                    email=order_email,
                    ref_code=create_ref_code(),
                    ordered_date=timezone.now(),
                    amount=discounted_total,
                )

            # Delivery fee calculation (single shared block)
            base_price = 0
            base = DeliveryBase.objects.first()
            if base:
                base_price = base.price or 0
            else:
                base_price = 3000

            city_clean  = address.city.strip().title()
            state_clean = address.state.strip().title()

            tenant_obj  = Client.objects.get(schema_name=tenant.schema_name)
            origin      = f"{tenant_obj.street_address} {tenant_obj.city} {tenant_obj.state}"
            destination = f"{address.street_address} {address.city} {address.state}"

            if state_clean.lower() == 'lagos':
                distance_result = get_delivery_distance(origin, destination)
                if distance_result:
                    distance_km, duration_min = distance_result
                    order.delivery_fee = round(
                        base_price + (distance_km * 50) + (duration_min * 20), 0
                    )
                else:
                    messages.error(request, "We don't deliver to that location.")
                    return redirect('checkout')
            else:
                delivery = DeliveryState.objects.filter(name__icontains=state_clean).first()
                if delivery:
                    order.delivery_fee = delivery.fixed_price
                else:
                    messages.error(request, "We do not deliver to that state.")
                    return redirect('checkout')

            order.amount = discounted_total + order.delivery_fee
            order.cart.set(cart_items)
            order.save()

            request.session['address_id'] = address.id
            messages.success(request, "Address confirmed. Proceed to payment.")
            return redirect('paym')

    return render(request, 'whiteecom/shop/checkoutpage.html', {
        'default_address_s': default_address_s,
        'subtotal': subtotal,
        'coupon_amount': coupon_amount,
        'total': discounted_total,
    })





# @ratelimit(key='ip', rate='10/m', block=True)
# def pickupform(request):

    
#     if request.user.is_authenticated:
#         cart_items = Cart.objects.filter(user=request.user, ordered=False)
#     else:
#         cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)
    
#     if not cart_items:
#         return redirect('cart_view')

   
#     if request.user.is_authenticated:
#         order = Order.objects.filter(user=request.user, Paid=False).last()
#     else:
#         order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

#     if order and order.coupon:
#         total_amount = sum(item.get_final_price() for item in cart_items)
       
#         tt= order.coupon.amount
#         if total_amount <= tt:
#             messages.error(request, f"You can't order anything below the promo or equal to the promo, amount: {order.coupon.amount}")
#             return redirect('cart_view')
#         total_amountss= total_amount-tt
#     else:
#         tt=None   

       
#         total_amount = sum(item.get_final_price() for item in cart_items)
#         total_amountss= sum(item.get_final_price() for item in cart_items)

#     if request.method == 'POST':

#         if request.user.is_authenticated:
#             cart_items = Cart.objects.filter(user=request.user, ordered=False)
#         else:
#             cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)

   
#         if request.user.is_authenticated:
#             order = Order.objects.filter(user=request.user, Paid=False).last()
#         else:
#             order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

#         if order and order.coupon:
#             total_amount = sum(item.get_final_price() for item in cart_items)
        
#             tt= order.coupon.amount
#             if total_amount <= tt:
#                 messages.error(request, f"You can't order anything below the promo or equal to the promo, amount: {order.coupon.amount}")
#                 return redirect('cart_view')
#             total_amountss= total_amount-tt
#         else:
#             tt=None   

#             # ✅ Calculate total amount
#             total_amount = sum(item.get_final_price() for item in cart_items)
#             total_amountss= sum(item.get_final_price() for item in cart_items)


#         # ✅ Calculate total amount
#         total_amount = sum(item.get_final_price() for item in cart_items)

        
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         phone_number = request.POST.get('phone_number')


#         # ✅ Create address
#         if request.user.is_authenticated:
#             address = Address.objects.create(
#                 user=request.user,
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=request.user.email,
#                 phone_number=phone_number,
#                 default=False
#             )
#         else:
#             address = Address.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 session_key=request.session.session_key,
#                 phone_number=phone_number,
#                 default=False
#             )


            

#         # ✅ Create order and set amount
      
#         if order:
#                 order.address = address
#                 order.email = request.user.email if request.user.is_authenticated else email
#                 order.ref_code = create_ref_code()
#                 order.ordered_date = timezone.now()
#                 order.amount = total_amountss
#                 order.delivery_fee =0.0
#                 order.save()

#         else:
#                 order = Order.objects.create(
#                          user=request.user if request.user.is_authenticated else None,
#                          session_key=request.session.session_key,
#                           Paid=False,
#                           address=address,
#                           email= request.user.email if request.user.is_authenticated else email,
#                           ref_code=create_ref_code(),
#                           ordered_date=timezone.now(),
#                           delivery_fee =0.0,
#                           amount=total_amountss,


#                     )


        
#         order.cart.set(cart_items)
#         order.save()
    
        
#         return redirect('paym')  # change as needed

#     return render(request, 'whiteecom/shop/pickup.html', { 'total_amount':total_amount,'tt':tt,'total_amountss':total_amountss})

    


@ratelimit(key='ip', rate='10/m', block=True)
def addcoupon(request):
    from ecom.models import Order, Coupon

    if request.method != 'POST':
        return redirect('cart_view')

    tenant = request.tenant
    code = request.POST.get('promo')

    with schema_context(tenant.schema_name):
        coupon = get_coupon(request, code)  # must also run inside schema_context

        if not coupon:
            messages.info(request, "This coupon does not exist.")
            return redirect('cart_view')

        # Build lookup filter — authenticated users never match on session_key
        if request.user.is_authenticated:
            order_filter = {'user': request.user, 'Paid': False}
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            order_filter = {'user': None, 'session_key': session_key, 'Paid': False}

        order, created = Order.objects.get_or_create(
            **order_filter,
            defaults={'coupon': coupon}
        )

        # Order already existed — update coupon if different
        if not created and order.coupon != coupon:
            order.coupon = coupon
            order.save()

        messages.success(request, "Coupon applied successfully!")

    return redirect('cart_view')

# === FLUTTERWAVE CONFIG ===
FLW_SECRET_KEY = settings.FLW_SECRET_KEY  # Replace with your own
BASE_URL = settings.BASE_URL

from b_manager.models import Client

# === CREATE PAYMENT ===
# @ratelimit(key='ip', rate='10/m', block=True)
# @csrf_exempt
# def create_payment(request):

#     # Get order
#     if request.user.is_authenticated:
#         order = Order.objects.filter(user=request.user, Paid=False).last()
#     else:
#         order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

#     if not order:
#         messages.error(request, "No active order found.")
#         return redirect("checkout")

#     if request.method in ["POST", "GET"]:

#         tenant = Client.objects.get(schema_name=request.tenant.schema_name)
#         subaccount_id = tenant.flutterwave_subaccount_id

#         email = order.email
#         amount = float(order.amount)

#         # --- SPLIT LOGIC ---
#         # Subaccount gets 98.9%
#         # You get 1.1%# Calculate your 1.1% commission

#         your_commission = round(amount * 0.989, 2)

#         # Subaccount gets the rest
#         sub_amount = round(amount - your_commission, 2)


#         tx_ref = order.ref_code
#         redirect_url = request.build_absolute_uri(reverse("verify_payment"))

#         payload = {
#             "tx_ref": tx_ref,
#             "amount": amount,
#             "currency": "NGN",
#             "redirect_url": redirect_url,

#             "customer": {
#                 "email": email,
#             },

#             # --- CORRECT FLUTTERWAVE SPLIT FIELD ---
#             "subaccounts": [
#                 {
#                     "id": subaccount_id,
#                     "transaction_charge_type": "flat",  # ALWAYS THIS
#                     "transaction_charge": sub_amount,              # AMOUNT, NOT %
#                 }
#             ],

#             "customizations": {
#                 "title": tenant.business_name,
#                 "description": tenant.business_description,
#             }
#         }

#         headers = {
#             "Authorization": f"Bearer {FLW_SECRET_KEY}",
#             "Content-Type": "application/json"
#         }

#         response = requests.post(f"{BASE_URL}/payments", headers=headers, data=json.dumps(payload))
#         res = response.json()

#         if res.get("status") == "success":
#             return redirect(res["data"]["link"])
#         else:
#             return JsonResponse(res)
#     messages.error(request, "fill your checkout form properly.")
#     return redirect("checkout")


# # === VERIFY PAYMENT ===
# @ratelimit(key='ip', rate='10/m', block=True)
# def verify_payment(request):
#     status = request.GET.get("status")
#     tx_ref = request.GET.get("tx_ref")

#     # Validate tx_ref
#     if not tx_ref:
#         return render(request, "whiteecom/shop/payment_failed.html",
#                       {"message": "Missing transaction reference"})

#     # Get order (user or guest)
#     if request.user.is_authenticated:
#         order = Order.objects.filter(user=request.user, Paid=False).last()
#     else:
#         order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

#     if not order:
#         messages.error(request, "No pending order to verify.")
#         return redirect("checkout")

#     # ---- Cancelled Payment ----
#     if status == "cancelled":
#         messages.warning(request, "Payment was cancelled.")
#         return render(request, "whiteecom/shop/payment_failed.html")

#     # ---- Verify with Flutterwave ----
#     verify_url = f"{BASE_URL}/transactions/verify_by_reference?tx_ref={tx_ref}"
#     headers = {
#         "Authorization": f"Bearer {FLW_SECRET_KEY}",
#     }

#     response = requests.get(verify_url, headers=headers).json()

#     # Flutterwave verification failed
#     if response.get("status") != "success":
#         return render(request, "whiteecom/shop/payment_failed.html",
#                       {"message": "Payment verification failed."})

#     data = response["data"]

#     # ---- Payment Successful? ----
#     if data["status"] == "successful":
#         flutter_amount = Decimal(str(data["amount"]))
#         order_amount = Decimal(str(order.amount))

#         # Verify the actual amount
#         if flutter_amount != order_amount:
#             return render(request, "whiteecom/shop/payment_failed.html",
#                           {"message": "Payment amount mismatch."})

#         # ---- Mark Order as Paid ----
#         order.Paid = True
#         order.ordered_date = timezone.now()
#         order.status = "shipping" 
#         order.save()

        
#         for cart_item in order.cart.all(): 
#             product = cart_item.product 
#             if product.quantity >= cart_item.quantity: 
#                 product.quantity -= cart_item.quantity 
#                 product.save() 
#             else: # # Just in case — avoid negative stock 
#                 product.quantity = 0 
#                 product.save() 

#         # ---- Update and Clear Cart ----
#         if request.user.is_authenticated:
#             Order.objects.filter(user=request.user, Paid=False).update(Paid=True)
#             Order.objects.filter(user=request.user, Paid=False).delete()
#         else:
#             Order.objects.filter(session_key=request.session.session_key, Paid=False).update(Paid=True)
#             Order.objects.filter(session_key=request.session.session_key, Paid=False).delete()

#         if request.user.is_authenticated:
#             Cart.objects.filter(user=request.user, ordered=False).update(ordered=True)
#             Cart.objects.filter(user=request.user, ordered=False).delete()
#         else:
#             Cart.objects.filter(session_key=request.session.session_key, ordered=False).update(ordered=True)
#             Cart.objects.filter(session_key=request.session.session_key, ordered=False).delete()

#         messages.success(request, "Payment successful!")
#         return redirect("paysuc")

#     # ---- Otherwise treat as failed ----
#     return render(request, "whiteecom/shop/payment_failed.html",
#                   {"message": "Payment not completed."})

    



# Paystack Configuration
PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = settings.PAYSTACK_BASE_URL


@ratelimit(key='ip', rate='10/m', block=True)
@csrf_exempt
def create_payment(request):
    # Get order
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    if not order:
        messages.error(request, "No active order found.")
        return redirect("checkout")

    if request.method in ["POST", "GET"]:
        tenant = Client.objects.get(schema_name=request.tenant.schema_name)

        email = order.email
        amount = int(float(order.amount) * 100)  # Paystack uses kobo (amount in minor units)
        reference = order.ref_code
        callback_url = request.build_absolute_uri(reverse("verify_payment"))

        payload = {
            "email": email,
            "amount": amount,  # Amount in kobo
            "currency": "NGN",
            "reference": reference,
            "callback_url": callback_url,
            
            "metadata": {
                "custom_fields": [
                    {
                        "display_name": "Business Name",
                        "variable_name": "business_name",
                        "value": tenant.business_name
                    },
                    {
                        "display_name": "Order ID",
                        "variable_name": "order_id",
                        "value": str(order.id)
                    }
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            headers=headers,
            data=json.dumps(payload)
        )
        res = response.json()

        if res.get("status") == True:  # Paystack uses boolean True
            return redirect(res["data"]["authorization_url"])
        else:
            messages.error(request, "Payment initialization failed.")
            return JsonResponse(res)
    
    messages.error(request, "Fill your checkout form properly.")
    return redirect("checkout")


# === VERIFY PAYMENT ===
@ratelimit(key='ip', rate='10/m', block=True)
def verify_payment(request):
    reference = request.GET.get("reference")
    
    # Handle cancelled payments
    if not reference:
        messages.warning(request, "Payment was cancelled.")
        return render(request, "whiteecom/shop/payment_failed.html")

    # Get order (user or guest)
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    if not order:
        messages.error(request, "No pending order to verify.")
        return redirect("checkout")

    # ---- Verify with Paystack ----
    verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(verify_url, headers=headers)
    res = response.json()

    # Paystack verification failed
    if res.get("status") != True:
        return render(request, "whiteecom/shop/payment_failed.html",
                      {"message": "Payment verification failed."})

    data = res["data"]

    # ---- Payment Successful? ----
    if data["status"] == "success":
        paystack_amount = Decimal(str(data["amount"])) / 100  # Convert from kobo to naira
        order_amount = Decimal(str(order.amount))

        # Verify the actual amount
        if paystack_amount != order_amount:
            return render(request, "whiteecom/shop/payment_failed.html",
                          {"message": "Payment amount mismatch."})

        # ---- Mark Order as Paid ----
        order.Paid = True
        order.ordered_date = timezone.now()
        order.status = "shipping"
        order.save()

        customer_first_name = order.address.first_name
        customer_last_name = order.address.last_name
        customer_email = order.address.email
        customer_num = order.address.phone_number


        three_percent = order.amount * 0.025

        # Apply condition
        if three_percent > 5000:
            final_amount = order.amount - 5000
        else:
            final_amount = round(order.amount * 0.975, 0)
        
        trans = Trans.objects.create(
            order=order,
            amount=final_amount
        )
        tttt =order.amount - final_amount
        send_mail(
                subject=f"New Order Paid",
                message=f"""
        A Customer just Paid, their details.

        Customer first name : {customer_first_name}
        Customer last Name: {customer_last_name}
        Amount paid: ₦{order.amount}
        Commision Paid to Baxting: ₦{tttt}
        Final Amount to receive into your account: ₦{final_amount}
        Customer Email: {customer_email}
        Customer Phone Number: {customer_num}
       
        """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.tenant.email ],   # <-- your email here
                fail_silently=False,
            )
        send_mail(
                subject=f"New Order Paid {request.tenant}",
                message=f"""
        A Customer just Paid, their details.

        Customer first name : {customer_first_name}
        Customer last Name: {customer_last_name}
        Amount paid: ₦{order.amount}
        Commision Paid to Baxting: ₦{tttt}
        Final Amount to receive into your account: ₦{final_amount}
        Customer Email: {customer_email}
        Customer Phone Number: {customer_num}
       
        """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER ],   # <-- your email here
                fail_silently=False,
            )


        # ---- Update Product Quantities ----
        for cart_item in order.cart.all():
            product = cart_item.product
            if product.quantity >= cart_item.quantity:
                product.quantity -= cart_item.quantity
                product.save()
            else:
                # Avoid negative stock
                product.quantity = 0
                product.save()

        # ---- Update and Clear Cart ----
        if request.user.is_authenticated:
            Order.objects.filter(user=request.user, Paid=False).update(Paid=True)
            Order.objects.filter(user=request.user, Paid=False).delete()
        else:
            Order.objects.filter(session_key=request.session.session_key, Paid=False).update(Paid=True)
            Order.objects.filter(session_key=request.session.session_key, Paid=False).delete()

        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user, ordered=False).update(ordered=True)
            Cart.objects.filter(user=request.user, ordered=False).delete()
        else:
            Cart.objects.filter(session_key=request.session.session_key, ordered=False).update(ordered=True)
            Cart.objects.filter(session_key=request.session.session_key, ordered=False).delete()

        messages.success(request, "Payment successful!")
        return redirect("paysuc")

    # ---- Otherwise treat as failed ----
    return render(request, "whiteecom/shop/payment_failed.html",
                  {"message": "Payment not completed."})
    


# def create_test_subaccount(request):
#     url = "https://api.paystack.co/subaccount"

#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "business_name": "Test Vendor Shop",
#         "bank_code": "057",                  # Zenith Bank (works)
#         "account_number": "0000000000",      # Universal test account
#         "percentage_charge": 50              # Your split percentage
#     }

#     response = requests.post(url, json=data, headers=headers)
#     return JsonResponse(response.json(), safe=False)




#     tx_ref = request.GET.get("tx_ref")
#     status = request.GET.get("status")

#     if not tx_ref:
#         return render(request, "whiteecom/shop/payment_failed.html", {"message": "Missing transaction reference"})
#     # for item in order.cart.all():
#     #         item.ordered = True
#     #         item.save()

#     # Verify transaction from Flutterwave API
#     headers = {
#         "Authorization": f"Bearer {FLW_SECRET_KEY}",
#     }

#     verify_url = f"{BASE_URL}/transactions/verify_by_reference?tx_ref={tx_ref}"
#     response = requests.get(verify_url, headers=headers)
#     res = response.json()

#     if res.get("status") == "success" and res["data"]["status"] == "successful":
#         # ✅ Payment verified successfully
#         amount = res["data"]["amount"]
#         customer_email = res["data"]["customer"]["email"]
#         tx_id = res["data"]["id"]

#         if order.delivery_fee != 0.0:
#             order.status="shipping"
#             order.save()

#         # Mark order as paid
#         order.Paid = True
#         order.ordered_date = timezone.now()
#         order.save()

#         # ✅ Reduce product stock
#         # for cart_item in order.cart.all():
#         #     product = cart_item.product
#         #     if product.quantity >= cart_item.quantity:
#         #         product.quantity -= cart_item.quantity
#         #         product.save()
#         #     else:
#         #         # Just in case — avoid negative stock
#         #         product.quantity = 0
#         #         product.save()

#         # Only mark this user's cart items as ordered
#         if request.user.is_authenticated:
#             Cart.objects.filter(user=request.user, ordered=False).update(ordered=True)
#         else:
#             Cart.objects.filter(session_key=request.session.session_key, ordered=False).update(ordered=True)

#         # Only delete remaining cart items for this user/session
#         if request.user.is_authenticated:
#             Cart.objects.filter(user=request.user, ordered=False).delete()
#         else:
#             Cart.objects.filter(session_key=request.session.session_key, ordered=False).delete()


        




            

#         otime=order.ordered_date

#         # ✅ Show success page
#         context = {
#             "amount": amount,
#             "email": customer_email,
#             "tx_id": tx_id,
#             "ref": tx_ref,
#             'otime':otime,
#         }
#         return redirect('paysuc')

#     else:
#         return render(request, "whiteecom/shop/payment_failed.html", {"message": "Payment verification failed"})



@ratelimit(key='ip', rate='10/m', block=True)
def ordderlist(request):
    from ecom.models import Order

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        base_qs = (
            Order.objects
            .select_related('address', 'user', 'coupon')
            .prefetch_related(
                'cart__product',
                'cart__product__category'
            )
            .order_by('-ordered_date')
        )

        if request.user.is_authenticated:
            orders = base_qs.filter(user=request.user, Paid=True)
        else:
            session_key = request.session.session_key
            if not session_key:
                orders = Order.objects.none()
            else:
                orders = base_qs.filter(session_key=session_key, Paid=True)

    return render(request, 'whiteecom/shop/orderlist.html', {'orders': orders})


@ratelimit(key='ip', rate='10/m', block=True)
def orderdet(request, id):
    from ecom.models import Order

    tenant = request.tenant

    with schema_context(tenant.schema_name):
        order = get_object_or_404(Order, id=id)

        # Ownership check — users can only view their own orders
        if request.user.is_authenticated:
            if order.user != request.user:
                messages.warning(request, "You do not have permission to view this order.")
                return redirect('order_list')
        else:
            session_key = request.session.session_key
            if not session_key or order.session_key != session_key:
                messages.warning(request, "You do not have permission to view this order.")
                return redirect('order_list')

        # Evaluate once to avoid repeated DB hits
        cart_items = list(
            order.cart.select_related('product').all()
        )

        # Use discount_price where available, fall back to full price
        total_price = sum(
            (item.product.discount_price or item.product.price) * item.quantity
            for item in cart_items
        )

        promo_discount = order.coupon.amount if order.coupon else 0
        grand_total = max(total_price - promo_discount, 0)

    context = {
        'order': order,
        'cart_items': cart_items,
        'total_price': total_price,
        'promo_discount': promo_discount,
        'grand_total': grand_total,
    }

    return render(request, 'whiteecom/shop/orderdet.html', context)






@ratelimit(key='ip', rate='10/m', block=True)
def search(request):
    from ecom.models import Product

    tenant = request.tenant

    query = request.GET.get('q', '').strip()

    with schema_context(tenant.schema_name):
        if query:
            products = (
                Product.objects
                .select_related('category')
                .filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query)
                )
                .distinct()
            )
        else:
            products = Product.objects.none()

    return render(request, 'whiteecom/shop/search_result.html', {
        'products': products,
        'query': query,       # useful for displaying "results for X" in template
    })




@ratelimit(key='ip', rate='10/m', block=True)
def paym(request):
    # Get cart items
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, ordered=False)
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    # No items or no order → redirect
    if not cart_items.exists():
        messages.error(request, "No item in cart.")
        return redirect('cart_view')

    if not order:
        messages.error(request, "No active order found.")
        return redirect('cart_view')

    # ---- 💰 CALCULATIONS ----
    # Subtotal (sum of all cart items)
    subtotal = sum(item.get_final_price() for item in cart_items)

    # Coupon / promo
    promo_discount = order.coupon.amount if order.coupon else 0

    # Prevent coupon from exceeding subtotal
    if subtotal <= promo_discount:
        messages.error(request, f"You can't order anything below or equal to your promo amount ({promo_discount}).")
        return redirect('cart_view')

    # Discounted total (after applying coupon)
    discounted_total = subtotal - promo_discount

    # Delivery fee (comes from order or logic)
    delivery_fee = order.delivery_fee or 0

    # Final grand total
    grand_total =  order.amount





    # ---- 📦 CONTEXT ----
    context = {
        'cart_items': cart_items,
        'order': order,
        'subtotal': subtotal,
        'promo_discount': promo_discount,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
    }

    return render(request, 'whiteecom/shop/payment.html', context)








@ratelimit(key='ip', rate='10/m', block=True)
def paydelivery(request):



    from ecom.models import Coupon, Category, Product,Cart, Address, DeliveryBase, DeliveryState,DeliveryCity,Order,Sale,Trans


    # Ensure session exists for guest users
    if not request.session.session_key:
        request.session.create()

    # ---------------- GET ACTIVE ORDER ----------------
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(
            session_key=request.session.session_key,
            Paid=False
        ).last()

    if not order:
        messages.error(request, "No active order found.")
        return redirect("home")

    if not order.address:
        messages.error(request, "Please add a delivery address.")
        return redirect("checkout")

    # ---------------- GET CART ITEMS ----------------
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, ordered=False)
    else:
        cart_items = Cart.objects.filter(
            session_key=request.session.session_key,
            ordered=False
        )

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # ---------------- ATTACH CARTS TO ORDER ----------------
    order.cart.set(cart_items)

    # ---------------- UPDATE ORDER ----------------
    order.Paid = True
    order.deliv = True
    order.ordered_date = timezone.now()

    if order.delivery_fee and order.delivery_fee > 0:
        order.status = "shipping (payment on delivery)"
    else:
        order.status = "pay on delivery"

    if not order.ref_code:
        order.ref_code = create_ref_code()

    order.amount = order.get_total() + (order.delivery_fee or 0)
    order.save()

    # ---------------- MARK CARTS AS ORDERED ----------------
    cart_items.update(ordered=True)

    # ---------------- CUSTOMER DETAILS ----------------
    address = order.address
    customer_first_name = address.first_name or ""
    customer_last_name = address.last_name or ""
    customer_email = address.email or ""
    customer_num = address.phone_number or ""

    amount = order.amount

    # ---------------- EMAIL TENANT ----------------
    send_mail(
        subject="New Order (Pay on Delivery)",
        message=f"""
A new order has been placed (Pay on Delivery)

Customer: {customer_first_name} {customer_last_name}
Amount: ₦{amount}
Email: {customer_email}
Phone: {customer_num}
Ref: {order.ref_code}
        """,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.tenant.email],
        fail_silently=False,
    )

    # ---------------- EMAIL ADMIN ----------------
    send_mail(
        subject=f"New Order (Pay on Delivery) - {request.tenant}",
        message=f"""
A new order has been placed (Pay on Delivery)

Customer: {customer_first_name} {customer_last_name}
Amount: ₦{amount}
Email: {customer_email}
Phone: {customer_num}
Ref: {order.ref_code}
        """,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )

    return redirect("paysuc")

def paysuc(request):

    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=True).last()

    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=True).last()

            # ✅ Show success page

    amount = order.amount or (order.get_total() + order.delivery_fee)
    customer_email = order.email
    tx_id = order.ref_code
    context = {
            "amount": amount,
            "email": customer_email,
            "tx_id": tx_id,
            'otime':order.ordered_date,
        }
    return render(request, "whiteecom/shop/payment_success.html", context)
