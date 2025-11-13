

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



# from django_tenants.utils import get_tenant_model

# tenant = request.tenant  # This works if django-tenants is set up
# subaccount_id = tenant.flw_subaccount_id





@ratelimit(key='ip', rate='40/m', block=True)
def removecoupon(request):
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




@ratelimit(key='ip', rate='40/m', block=True)
def create_ref_code():
    return ' '.join(random.choices(string.ascii_lowercase + string.digits, k=20))




@ratelimit(key='ip', rate='40/m', block=True)
def get_coupon(request, code):
    try:
        return Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return None



@ratelimit(key='ip', rate='40/m', block=True)
def home(request):
    items = True
    product_list = Product.objects.filter(best_sellers=items).order_by('-id')  # newest first
    paginator = Paginator(product_list, 12)  # 👈 8 products per page (adjust as you like)

    page_number = request.GET.get('page')  # ?page=2
    products = paginator.get_page(page_number)
    
    return render(request, 'whiteecom/shop/home.html', {'products': products})



@ratelimit(key='ip', rate='40/m', block=True)
def product_list(request):
    product_list = Product.objects.all().order_by('-id')  # newest first
    paginator = Paginator(product_list, 12)  # 👈 8 products per page (adjust as you like)

    page_number = request.GET.get('page')  # ?page=2
    products = paginator.get_page(page_number)  # handles invalid or empty pages automatically

    return render(request, 'whiteecom/shop/shop.html', {'products': products})

@ratelimit(key='ip', rate='40/m', block=True)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    category = product.category

    # Get only the latest 4 products in the same category (excluding the current one)
    related_products = (
        Product.objects.filter(category=category)
        .exclude(id=product.id)
        .order_by('-created_at')[:4]  # assuming your model has a created_at field
    )

    return render(
        request,
        'whiteecom/shop/productdet.html',
        {'product': product, 'dud': related_products, }
    )


@ratelimit(key='ip', rate='40/m', block=True)
def remove_from(request, slug):
    product = get_object_or_404(Product, slug=slug)


    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(product=product, user=request.user, ordered=False).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")
    else:
        session_key = request.session.session_key or request.session.create()
        cart_item = Cart.objects.filter(product=product, session_key=session_key, ordered=False).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not in your cart.")

    # Redirect back to the cart page
    return redirect('productdet', slug=slug)  # or the URL name of your cart page


@ratelimit(key='ip', rate='40/m', block=True)
def cart_view(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, ordered=False)
    else:
        cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)

    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    if order and order.coupon:
        total_amount = sum(item.get_final_price() for item in cart_items)
        tt = order.coupon.amount

        if total_amount <= tt:
            total_amountss = 0  # prevent negative totals
        else:
            total_amountss = total_amount - tt
    else:
        tt = None
        total_amount = sum(item.get_final_price() for item in cart_items)
        total_amountss = total_amount

    # Re-fetch cart items in proper order
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, ordered=False).order_by('-id')
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = Cart.objects.filter(session_key=session_key, ordered=False).order_by('-id')

    total = sum(item.get_final_price() for item in cart_items)

    return render(request, 'whiteecom/shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'total_amount': total_amount,
        'tt': tt,
        'total_amountss': total_amountss
    })



@ratelimit(key='ip', rate='40/m', block=True)
def add_to(request, slug):
    # Get the product
    product = get_object_or_404(Product, slug=slug)
    

    # Determine cart owner
    if request.user.is_authenticated:
        cart_filter = {'user': request.user, 'ordered': False, 'product': product}
    else:
        # For guest users, we use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_filter = {'session_key': session_key, 'ordered': False, 'product': product}

    # Check if item exists
    cart_item = Cart.objects.filter(**cart_filter).first()

    if cart_item:
        if product.quantity <= cart_item.quantity:
            messages.warning(request, f"{product.name} for that size  is only {product.quantity} we have left ")
            return redirect('cart_view')
            
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in your cart.")
    else:
        # Create new cart item
        
        cart_item = Cart.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product=product,
            ordered=False,
            session_key=request.session.session_key,
            quantity = 1)

        

    
    return redirect('cart_view')  # Replace with your cart page URL




@ratelimit(key='ip', rate='40/m', block=True)
def remove(request, slug):
    product = get_object_or_404(Product, slug=slug)


    if request.user.is_authenticated:
        cart_filter = {'user': request.user, 'ordered': False, 'product': product}
    else:
        # For guest users, we use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_filter = {'session_key': session_key, 'ordered': False, 'product': product}




    cart_item = Cart.objects.filter(**cart_filter).first()
    if cart_item:
        if cart_item.quantity <= 1 :
                cart_item.delete()
                messages.warning(request, f"cartitem is empyty")
                
                return redirect('cart_view')
                
        else:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, f"{product.name} quantity updated in your cart.")

        
    return redirect('cart_view')


@ratelimit(key='ip', rate='40/m', block=True)
def remove_item(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(product=product, user=request.user, ordered=False,).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")
    else:
        session_key = request.session.session_key or request.session.create()
        cart_item = Cart.objects.filter(product=product, session_key=session_key, ordered=False).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not in your cart.")
  

    # Redirect back to the cart page
    return redirect('cart_view')  # or the URL name of your cart page

@ratelimit(key='ip', rate='40/m', block=True)
def remove_all(request):
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user, ordered=False).delete()
    else:
        session_key = request.session.session_key
        if session_key:
            Cart.objects.filter(session_key=session_key, ordered=False).delete()
    messages.success(request, "All items removed from your cart.")
    return redirect('cart_view')












@ratelimit(key='ip', rate='40/m', block=True)
def checkout(request):
    default_address_s = None
    if request.user.is_authenticated:
        default_address_s = Address.objects.filter(user=request.user,default=True).first()
        
    else:
         default_address_s = Address.objects.filter(session_key=request.session.session_key,default=True).first()


    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, ordered=False)
    else:
        cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)
        
    if not cart_items:
        return redirect('cart_view')

   
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    if order and order.coupon:
        total_amount = sum(item.get_final_price() for item in cart_items)
       
        tt= order.coupon.amount
        if total_amount <= tt:
            messages.error(request, f"You can't order anything below the promo or equal to the promo, amount: {order.coupon.amount}")
            return redirect('cart_view')
        total_amountss= total_amount-tt
    else:
        tt=None   

        # ✅ Calculate total amount
        total_amount = sum(item.get_final_price() for item in cart_items)
        total_amountss= sum(item.get_final_price() for item in cart_items)

    
    if request.method == 'POST':
        # Checkbox values
        save_address = request.POST.get('save_address') == 'on'
        use_default = request.POST.get('use_default') == 'on'
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user, ordered=False)
        else:
            cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)

   
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, Paid=False).last()
        else:
            order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

        if order and order.coupon:
            total_amount = sum(item.get_final_price() for item in cart_items)
        
            tt= order.coupon.amount
            if total_amount <= tt:
                messages.error(request, f"You can't order anything below the promo or equal to the promo, amount: {order.coupon.amount}")
                return redirect('cart_view')
            total_amountss= total_amount-tt
        else:
            tt=None   

            # ✅ Calculate total amount
            total_amount = sum(item.get_final_price() for item in cart_items)
            total_amountss= sum(item.get_final_price() for item in cart_items)


        # ✅ Calculate total amount
        total_amount = sum(item.get_final_price() for item in cart_items)

        # If user has a default address and wants to use it
        if use_default and request.user.is_authenticated:
            try:
                default_address = Address.objects.get(user=request.user, default=True)
                request.session['address_id'] = default_address.id

                if order:
                    order.address = default_address
                    order.email = request.user.email if request.user.is_authenticated else email
                    order.ref_code = create_ref_code()
                    order.ordered_date = timezone.now()
                    order.amount = total_amountss
                    order.save()

                else:
                    order = Order.objects.create(
                         user=request.user if request.user.is_authenticated else None,
                         session_key=request.session.session_key,
                          Paid=False,
                          address=default_address,
                          email= request.user.email if request.user.is_authenticated else email,
                          ref_code=create_ref_code(),
                          ordered_date=timezone.now(),
                          amount=total_amountss,


                    )

                city = default_address.city.strip().title()
                state = default_address.state.strip().title()

                if state.lower() == 'lagos':
                    delivery = DeliveryCity.objects.filter(name__icontains=city).first()
                    if delivery:
                        order.delivery_fee = delivery.delivery_fee
                    else:
                        order.delivery_fee = 10000  # default Lagos fee
                else:
                    delivery = DeliveryState.objects.filter(name__icontains=state).first()
                    if delivery:
                        order.delivery_fee = delivery.fixed_price
                    else:
                        messages.error(request, "We do not deliver to that state")
                        return redirect('checkout')


                
                
                order.amount = total_amountss+order.delivery_fee


                order.save()







              
                order.cart.set(cart_items)
                order.save()




                messages.success(request, "Default address selected successfully.")
                return redirect('paym')  # change to your next step
            except Address.DoesNotExist:
                messages.warning(request, "You don’t have a default address yet.")
                return redirect('checkout')

        # Otherwise, collect form input
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        street_address = request.POST.get('street_address')
        apartment = request.POST.get('apartment')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')


        # ✅ Create address
        if request.user.is_authenticated:
            address = Address.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=request.user.email,
                street_address=street_address,
                apartment=apartment,
                city=city,
                state=state,
                country=country,
                phone_number=phone_number,
                default=False
            )
        else:
            address = Address.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                session_key=request.session.session_key,
                street_address=street_address,
                apartment=apartment,
                city=city,
                state=state,
                country=country,
                phone_number=phone_number,
                default=False
            )


        # if state.lower() == 'lagos':
        #     if


            

        # ✅ Create order and set amount
      
        if order:
                order.address = address
                order.email = request.user.email if request.user.is_authenticated else email
                order.ref_code = create_ref_code()
                order.ordered_date = timezone.now()
                order.amount = total_amountss
                order.save()

        else:
                order = Order.objects.create(
                         user=request.user if request.user.is_authenticated else None,
                         session_key=request.session.session_key,
                          Paid=False,
                          address=address,
                          email= request.user.email if request.user.is_authenticated else email,
                          ref_code=create_ref_code(),
                          ordered_date=timezone.now(),
                          amount=total_amountss,


                    )


        city = city.strip().title()
        state = state.strip().title()

        if state.lower() == 'lagos':
            delivery = DeliveryCity.objects.filter(name__icontains=city).first()
            if delivery:
                order.delivery_fee = delivery.delivery_fee
            else:
                order.delivery_fee = 10000  # default Lagos fee
        else:
            delivery = DeliveryState.objects.filter(name__icontains=state).first()
            if delivery:
                order.delivery_fee = delivery.fixed_price
            else:
                messages.error(request, "We do not deliver to that state")
                return redirect('checkout')
        
        order.amount = total_amountss+order.delivery_fee

        order.save()



                
            
            



        
        # ✅ Attach cart items to order
        order.cart.set(cart_items)
        order.save()
    
        

        # Save this address as default if checked
        if save_address and request.user.is_authenticated:
            # unset any previous default
            Address.objects.filter(user=request.user, default=True).update(default=False)
            address.default = True
            address.save()
            messages.success(request, "Address saved as your default address.")
        elif save_address and not request.user.is_authenticated:
            messages.info(request, "Address saved to that order .")

        # Save address id in session (for order/payment)
        request.session['address_id'] = address.id

        messages.success(request, "Address confirmed. Proceed to payment.")
        return redirect('paym')  # change as needed

    return render(request, 'whiteecom/shop/checkoutpage.html', {'default_address_s':default_address_s, 'total_amount':total_amount,'tt':tt,'total_amountss':total_amountss})







@ratelimit(key='ip', rate='40/m', block=True)
def pickupform(request):

    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, ordered=False)
    else:
        cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)
    
    if not cart_items:
        return redirect('cart_view')

   
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    if order and order.coupon:
        total_amount = sum(item.get_final_price() for item in cart_items)
       
        tt= order.coupon.amount
        if total_amount <= tt:
            messages.error(request, f"You can't order anything below the promo or equal to the promo, amount: {order.coupon.amount}")
            return redirect('cart_view')
        total_amountss= total_amount-tt
    else:
        tt=None   

       
        total_amount = sum(item.get_final_price() for item in cart_items)
        total_amountss= sum(item.get_final_price() for item in cart_items)

    if request.method == 'POST':

        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user, ordered=False)
        else:
            cart_items = Cart.objects.filter(session_key=request.session.session_key, ordered=False)

   
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, Paid=False).last()
        else:
            order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

        if order and order.coupon:
            total_amount = sum(item.get_final_price() for item in cart_items)
        
            tt= order.coupon.amount
            if total_amount <= tt:
                messages.error(request, f"You can't order anything below the promo or equal to the promo, amount: {order.coupon.amount}")
                return redirect('cart_view')
            total_amountss= total_amount-tt
        else:
            tt=None   

            # ✅ Calculate total amount
            total_amount = sum(item.get_final_price() for item in cart_items)
            total_amountss= sum(item.get_final_price() for item in cart_items)


        # ✅ Calculate total amount
        total_amount = sum(item.get_final_price() for item in cart_items)

        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')


        # ✅ Create address
        if request.user.is_authenticated:
            address = Address.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=request.user.email,
                phone_number=phone_number,
                default=False
            )
        else:
            address = Address.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                session_key=request.session.session_key,
                phone_number=phone_number,
                default=False
            )


            

        # ✅ Create order and set amount
      
        if order:
                order.address = address
                order.email = request.user.email if request.user.is_authenticated else email
                order.ref_code = create_ref_code()
                order.ordered_date = timezone.now()
                order.amount = total_amountss
                order.delivery_fee =0.0
                order.save()

        else:
                order = Order.objects.create(
                         user=request.user if request.user.is_authenticated else None,
                         session_key=request.session.session_key,
                          Paid=False,
                          address=address,
                          email= request.user.email if request.user.is_authenticated else email,
                          ref_code=create_ref_code(),
                          ordered_date=timezone.now(),
                          delivery_fee =0.0,
                          amount=total_amountss,


                    )


        
        order.cart.set(cart_items)
        order.save()
    
        
        return redirect('paym')  # change as needed

    return render(request, 'whiteecom/shop/pickup.html', { 'total_amount':total_amount,'tt':tt,'total_amountss':total_amountss})

    


@ratelimit(key='ip', rate='40/m', block=True)
def addcoupon(request):
    if request.method == 'POST':
        code = request.POST.get('promo')
        coupon = get_coupon(request, code)
        
        if not coupon:
            messages.info(request, "This coupon does not exist")
            return redirect('checkout')

        if request.user.is_authenticated:
            order, created = Order.objects.get_or_create(
                user=request.user,
                session_key=request.session.session_key,
                Paid=False,
                defaults={'coupon': coupon}
            )
        else:
            order, created = Order.objects.get_or_create(
                user=None,
                session_key=request.session.session_key,
                Paid=False,
                defaults={'coupon': coupon}
            )

        # If order exists but no coupon yet, assign it
        if not created and order.coupon != coupon:
            order.coupon = coupon
            order.save()

        messages.success(request, "Coupon applied successfully!")
        return redirect('cart_view')

    return redirect('cart_views')


# === FLUTTERWAVE CONFIG ===
FLW_SECRET_KEY = settings.FLW_SECRET_KEY  # Replace with your own
BASE_URL = settings.BASE_URL



# === CREATE PAYMENT ===
@ratelimit(key='ip', rate='40/m', block=True)
@csrf_exempt
def create_payment(request):


    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user,Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()


    if request.method in ["POST", "GET"]:


        email = order.email
        amount = order.amount

        # Your commission (1.1%) with a cap of ₦3000
        commission = min(float(amount) * 0.011, 3000)

        # Split payment config: 1.1% goes to you
        # Flutterwave automatically takes their 1.4%
        split = [
            {
                "subaccount": "RS_YOUR_SUBACCOUNT_ID",  # Replace with your subaccount ID
                "share": commission
            }
        ]

        tx_ref = order.ref_code

        # 👇 dynamically generate redirect URL based on current tenant domain
        redirect_url = request.build_absolute_uri(reverse("verify_payment"))


        payload = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": "NGN",
            "redirect_url": redirect_url,
            "customer": {
                "email": email,
            },
            "meta": {
                "split": split
            },
            "customizations": {
                "title": "E-commerce Split Payment Demo",
                "description": "Split transaction between main and subaccount",
            }
        }

        headers = {
            "Authorization": f"Bearer {FLW_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{BASE_URL}/payments", headers=headers, data=json.dumps(payload))
        res = response.json()


        if res.get("status") == "success":
            return redirect(res["data"]["link"])
        else:
            return JsonResponse(res)
    messages.error(request, "fill your checkout form properly.")
    return redirect("checkout")


# === VERIFY PAYMENT ===
@ratelimit(key='ip', rate='40/m', block=True)
def verify_payment(request):

    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user,Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()



    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user,ordered=False)
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key, ordered=False)


    





    tx_ref = request.GET.get("tx_ref")
    status = request.GET.get("status")

    if not tx_ref:
        return render(request, "whiteecom/shop/payment_failed.html", {"message": "Missing transaction reference"})
    # for item in order.cart.all():
    #         item.ordered = True
    #         item.save()

    # Verify transaction from Flutterwave API
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
    }

    verify_url = f"{BASE_URL}/transactions/verify_by_reference?tx_ref={tx_ref}"
    response = requests.get(verify_url, headers=headers)
    res = response.json()

    if res.get("status") == "success" and res["data"]["status"] == "successful":
        # ✅ Payment verified successfully
        amount = res["data"]["amount"]
        customer_email = res["data"]["customer"]["email"]
        tx_id = res["data"]["id"]

        if order.delivery_fee != 0.0:
            order.status="shipping"
            order.save()

        # Mark order as paid
        order.Paid = True
        order.ordered_date = timezone.now()
        order.save()

        # ✅ Reduce product stock
        for cart_item in order.cart.all():
            product = cart_item.product
            if product.quantity >= cart_item.quantity:
                product.quantity -= cart_item.quantity
                product.save()
            else:
                # Just in case — avoid negative stock
                product.quantity = 0
                product.save()

        # Only mark this user's cart items as ordered
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user, ordered=False).update(ordered=True)
        else:
            Cart.objects.filter(session_key=request.session.session_key, ordered=False).update(ordered=True)

        # Only delete remaining cart items for this user/session
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user, ordered=False).delete()
        else:
            Cart.objects.filter(session_key=request.session.session_key, ordered=False).delete()


        




            

        otime=order.ordered_date

        # ✅ Show success page
        context = {
            "amount": amount,
            "email": customer_email,
            "tx_id": tx_id,
            "ref": tx_ref,
            'otime':otime,
        }
        return render(request, "whiteecom/shop/payment_success.html", context)

    else:
        return render(request, "whiteecom/shop/payment_failed.html", {"message": "Payment verification failed"})



@ratelimit(key='ip', rate='40/m', block=True)
def ordderlist(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=True).order_by('-ordered_date')
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=True)

    context={
        'order':order,
    }
    return render(request, 'whiteecom/shop/orderlist.html',context)



@ratelimit(key='ip', rate='40/m', block=True)
def orderdet(request, id):
    order = get_object_or_404(Order, id=id)
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
        grand_total = 0  # prevent negative totals if promo is larger

    context = {
        'order': order,
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'promo_discount': promo_discount,
        'grand_total': grand_total,
    }

    return render(request, 'whiteecom/shop/orderdet.html', context)







@ratelimit(key='ip', rate='40/m', block=True)
def search(request):
    queryset = Product.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)

        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'whiteecom/shop/search_result.html', context)

@ratelimit(key='ip', rate='40/m', block=True)
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




