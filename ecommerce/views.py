

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




def create_ref_code():
    return ' '.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def get_coupon(request, code):
    try:
        return Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return None




def home(request):
    items = True
    product_list = Product.objects.filter(best_sellers=items).order_by('-id')  # newest first
    paginator = Paginator(product_list, 12)  # 👈 8 products per page (adjust as you like)

    page_number = request.GET.get('page')  # ?page=2
    products = paginator.get_page(page_number)
    
    return render(request, 'opeyemi/whiteecom/shop/home.html', {'products': products})



def product_list(request):
    product_list = Product.objects.all().order_by('-id')  # newest first
    paginator = Paginator(product_list, 12)  # 👈 8 products per page (adjust as you like)

    page_number = request.GET.get('page')  # ?page=2
    products = paginator.get_page(page_number)  # handles invalid or empty pages automatically

    return render(request, 'opeyemi/whiteecom/shop/shop.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    productss = ProductVariant.objects.filter(product=product)
    product_price = productss.first().price if productss.exists() else 0
    category = product.category

    # Get only the latest 4 products in the same category (excluding the current one)
    related_products = (
        Product.objects.filter(category=category)
        .exclude(id=product.id)
        .order_by('-created_at')[:4]  # assuming your model has a created_at field
    )

    return render(
        request,
        'opeyemi/whiteecom/shop/productdet.html',
        {'products': product, 'dud': related_products,'productss': productss, 'product_price':product_price}
    )








def remove_from(request, slug):
    product = get_object_or_404(Product, slug=slug)
    size_id = request.GET.get('size')  # use GET here
    size = get_object_or_404(Size, id=size_id) if size_id else None

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(product=product, user=request.user, ordered=False, size=size).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")
    else:
        session_key = request.session.session_key or request.session.create()
        cart_item = Cart.objects.filter(product=product, session_key=session_key, ordered=False, size=size).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not in your cart.")

    # Redirect back to the cart page
    return redirect('productdet', slug=slug)  # or the URL name of your cart page



def cart_view(request):
    if request.user.is_authenticated:
        # Logged-in users
        cart_items = Cart.objects.filter(user=request.user, ordered=False).order_by('-id')
    else:
        # Guest users
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = Cart.objects.filter(session_key=session_key, ordered=False).order_by('-id')

    total = 0
    for item in cart_items:
        try:
            variant = ProductVariant.objects.get(product=item.product, size=item.size)
            total += variant.price * item.quantity
        except ProductVariant.DoesNotExist:
            # In case variant is missing, skip or handle
            pass

    return render(request, 'opeyemi/whiteecom/shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })



def add_to(request, slug):
    # Get the product
    product = get_object_or_404(Product, slug=slug)
    
    # Get the selected size from POST data (or default if you want)
    size_id = request.POST.get('size')
    size = get_object_or_404(Size, id=size_id) if size_id else None

    product_variant = get_object_or_404(ProductVariant, size=size, product=product)

    # Determine cart owner
    if request.user.is_authenticated:
        cart_filter = {'user': request.user, 'ordered': False, 'product': product, 'size': size}
    else:
        # For guest users, we use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_filter = {'session_key': session_key, 'ordered': False, 'product': product, 'size': size}

    # Check if item exists
    cart_item = Cart.objects.filter(**cart_filter).first()

    if cart_item:
        if product_variant.quantity <= cart_item.quantity:
            messages.warning(request, f"{product.name} for that size  is only {product_variant.quantity} we have left ")
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
            size=size,
            quantity = 1)

        


    
    return redirect('cart_view')  # Replace with your cart page URL









def add(request, slug):
    product = get_object_or_404(Product, slug=slug)

    size_name = request.GET.get('size')
    size = get_object_or_404(Size, name=size_name) if size_name else None
    product_variant = get_object_or_404(ProductVariant, size=size, product=product)

    if request.user.is_authenticated:
        cart_filter = {'user': request.user, 'ordered': False, 'product': product, 'size': size}
    else:
        # For guest users, we use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_filter = {'session_key': session_key, 'ordered': False, 'product': product, 'size': size}




    cart_item = Cart.objects.filter(**cart_filter).first()
    if cart_item:
        if product_variant.quantity <= cart_item.quantity:
                messages.warning(request, f"{product.name} for that size  is only {product_variant.quantity} we have left ")
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
            size=size,
            quantity = 1
        )



        
    return redirect('cart_view')




def remove(request, slug):
    product = get_object_or_404(Product, slug=slug)

    size_name = request.GET.get('size')
    size = get_object_or_404(Size, name=size_name) if size_name else None
    product_variant = get_object_or_404(ProductVariant, size=size, product=product)

    if request.user.is_authenticated:
        cart_filter = {'user': request.user, 'ordered': False, 'product': product, 'size': size}
    else:
        # For guest users, we use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_filter = {'session_key': session_key, 'ordered': False, 'product': product, 'size': size}




    cart_item = Cart.objects.filter(**cart_filter).first()
    if cart_item:
        if cart_item.quantity <= 1 :
                cart_item.delete()
                messages.warning(request, f"cartitem is empyty")
                
                return redirect('cart_view')
                # 
        else:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, f"{product.name} quantity updated in your cart.")

        
    return redirect('cart_view')




def remove_item(request, slug):
    product = get_object_or_404(Product, slug=slug)
    size_id = request.GET.get('size')  # use GET here
    size = get_object_or_404(Size, name=size_id) if size_id else None

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(product=product, user=request.user, ordered=False, size=size).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not found in your cart.")
    else:
        session_key = request.session.session_key or request.session.create()
        cart_item = Cart.objects.filter(product=product, session_key=session_key, ordered=False, size=size).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.warning(request, f"{product.name} was not in your cart.")
  

    # Redirect back to the cart page
    return redirect('cartview')  # or the URL name of your cart page




def remove_all(request):
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user, ordered=False).delete()
    else:
        session_key = request.session.session_key
        if session_key:
            Cart.objects.filter(session_key=session_key, ordered=False).delete()
    messages.success(request, "All items removed from your cart.")
    return redirect('cart_view')














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

   
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=False).last()
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=False).last()

    if order and order.coupon:
        total_amount = sum(item.variant.price * item.quantity for item in cart_items)
       
        tt= order.coupon.amount
        if total_amount <= tt:
            messages.error(request, "You can't order anything below you promo or equal to the promo")
            return redirect('cart_view')
        total_amountss= total_amount-tt
    else:
        tt=None   

        # ✅ Calculate total amount
        total_amount = sum(item.variant.price * item.quantity for item in cart_items)
        total_amountss= sum(item.variant.price * item.quantity for item in cart_items)

    
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
            total_amount = sum(item.variant.price * item.quantity for item in cart_items)
        
            tt= order.coupon.amount
            if total_amount <= tt:
                messages.error(request, "You can't order anything below you promo or equal to the promo")
                return redirect('cart_view')
            total_amountss= total_amount-tt
        else:
            tt=None   

            # ✅ Calculate total amount
            total_amount = sum(item.variant.price * item.quantity for item in cart_items)
            total_amountss= sum(item.variant.price * item.quantity for item in cart_items)


        # ✅ Calculate total amount
        total_amount = sum(item.variant.price * item.quantity for item in cart_items)

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

              
                order.cart.set(cart_items)
                order.save()




                messages.success(request, "Default address selected successfully.")
                return redirect('create_payment')  # change to your next step
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
        return redirect('create_payment')  # change as needed

    return render(request, 'opeyemi/whiteecom/shop/checkoutpage.html', {'default_address_s':default_address_s, 'total_amount':total_amount,'tt':tt,'total_amountss':total_amountss})


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
        return redirect('checkout')

    return redirect('checkout')































# === FLUTTERWAVE CONFIG ===
FLW_SECRET_KEY = "FLWSECK_TEST-f12c4fc7f327b4839f9aec50aa750b94-X"  # Replace with your own
BASE_URL = "https://api.flutterwave.com/v3"



# === CREATE PAYMENT ===
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

        payload = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": "NGN",
            "redirect_url": "http://opestore.localhost:8000/verify_payment/",
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
        return render(request, "opeyemi/whiteecom/shop/payment_failed.html", {"message": "Missing transaction reference"})
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

        # Mark order as paid
        order.Paid = True
        order.ordered_date = timezone.now()
        order.save()

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
        return render(request, "opeyemi/whiteecom/shop/payment_success.html", context)

    else:
        return render(request, "opeyemi/whiteecom/shop/payment_failed.html", {"message": "Payment verification failed"})








def ordderlist(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, Paid=True)
    else:
        order = Order.objects.filter(session_key=request.session.session_key, Paid=True)

    context={
        'order':order,
    }
    return render(request, 'opeyemi/whiteecom/shop/orderlist.html',context)




def orderdet(request, id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=id)
    else:
        order = get_object_or_404(Order, id=id)


    context={
        'order':order,
    }
    return render(request, 'opeyemi/whiteecom/shop/orderdet.html',context)









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
    return render(request, 'opeyemi/whiteecom/shop/search_result.html', context)







