

from cloudinary.models import CloudinaryField


from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator 
# Create your models here.
from django.db import models

from colorfield.fields import ColorField 

from django.conf import settings
from django.utils.text import slugify


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount= models.FloatField()
    def __str__(self):
        return self.code


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)


       
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name













class Product(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    slug = models.SlugField(unique=True,null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    size = models.CharField(max_length=50,null=True, blank=True)
    color = models.CharField(max_length=50,null=True, blank=True)
    quantity = models.IntegerField(blank=True, null=True)

    # image = models.ImageField( upload_to='ecom/',null=True, blank=True)
    image = CloudinaryField(folder='ecom', null=True, blank=True)
    best_sellers = models.BooleanField(default=False,)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("productdet", kwargs={
            'slug':self.slug
        })

    

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True) 
    
    quantity = models.IntegerField(default=1,validators=[MinValueValidator(0)])
    ordered = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.product.name} - {self.product.size} ({self.quantity} pcs)"
    def get_total_item_price(self):
        return self.quantity * self.product.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()
    
    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True, blank=True)

    session_key = models.CharField(max_length=40, null=True, blank=True) 

    first_name = models.CharField(max_length=100,blank=True, null=True)
    last_name = models.CharField(max_length=100,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    street_address = models.CharField(max_length=100,blank=True, null=True)
    apartment = models.CharField(max_length=100,blank=True, null=True)
    city = models.CharField(max_length=100,blank=True, null=True)
    state = models.CharField(max_length=100,blank=True, null=True)

    country = models.CharField(max_length=100,blank=True, null=True)
    phone_number = models.CharField(max_length=100,blank=True, null=True)
    default = models.BooleanField(default=False)





class DeliveryState(models.Model):
    """
    Each state in Nigeria. Some may have multiple cities/LGAs with different prices.
    """
    name = models.CharField(max_length=100, unique=True)
    has_local_government = models.BooleanField(default=False, help_text="If true, use city-level pricing for this state.")
    fixed_price = models.FloatField(blank=True, null=True, help_text="put only figures eg(50000).")

    def __str__(self):
        return self.name


class DeliveryCity(models.Model):
    """
    Cities or LGAs that belong to a state (only used if the state has_local_government=True)
    """
    state = models.ForeignKey(DeliveryState, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)
    delivery_fee = models.FloatField()

    class Meta:
        unique_together = ('state', 'name')

    def save(self, *args, **kwargs):
        # Automatically link to "Lagos" state
        from django.core.exceptions import ObjectDoesNotExist

        try:
            lagos_state = DeliveryState.objects.get(name__icontains="Lagos")
        except ObjectDoesNotExist:
            # If Lagos doesn’t exist, create it automatically
            lagos_state = DeliveryState.objects.create(name="Lagos", has_local_government=True)

        self.state = lagos_state
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.state.name}"

    def __str__(self):
        return f"{self.name}, {self.state.name}"





DELIVERY_OPTIONS = [
    ('pickup', 'Pick up from store (₦0)'),
    ('door', 'Deliver to my address'),
]

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    ref_code = models.CharField(max_length=100)
    cart = models.ManyToManyField(Cart)
    session_key = models.CharField(max_length=40, null=True, blank=True) 
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True) 
    amount = models.FloatField(null=True, blank=True)
    Paid = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(default='pick it up at the store')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    delivery_fee = models.FloatField(default=0.0)


    def __str__(self):
        return f"{self.email}"
    def get_subtotal(self):
        """Sum of all cart items"""
        total = 0
        for cart_item in self.cart.all():
            total += cart_item.get_final_price()
        return total

    def get_discount_amount(self):
        """Coupon discount amount"""
        if self.coupon:
            return self.coupon.amount
        return 0

    def get_total(self):
        """Subtotal minus coupon"""
        subtotal = self.get_subtotal()
        discount = self.get_discount_amount()
        return subtotal - discount
    
    def get_absolute_urlss(self):
        return reverse("orderdet", kwargs={"id": self.id})


