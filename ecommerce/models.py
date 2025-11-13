# from django.db import models
# from django.urls import reverse
# from django.core.validators import MinValueValidator 
# # Create your models here.
# from django.db import models

# from colorfield.fields import ColorField 

# from django.conf import settings
# from django.utils.text import slugify


# class Coupon(models.Model):
#     code = models.CharField(max_length=15)
#     amount= models.FloatField()
#     def __str__(self):
#         return self.code


# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)


       
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base_slug = slugify(self.name)
#             slug = base_slug
#             counter = 1
#             while Category.objects.filter(slug=slug).exists():
#                 slug = f"{base_slug}-{counter}"
#                 counter += 1
#             self.slug = slug
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name

        
# SIZE_CATEGORIES = [
#         ('S', 'S '),
#         ('M', 'M'),
#         ('L', 'L'),
#         ('XL', 'XL'),
#         ('XXL', '	XXL'),]


# class Size(models.Model):
#     name = models.CharField(max_length=100, choices=SIZE_CATEGORIES, blank=True, null=True)


#     def __str__(self):
#         return self.name
    
# # class Color(models.Model):
# #     name = models.CharField(max_length=100)
# #     color = ColorField(default='#000000') 
    
# #     def __str__(self):
# #         return self.name

# class Product(models.Model):
#     name = models.CharField(max_length=100,null=True, blank=True)
#     slug = models.SlugField(unique=True,null=True, blank=True)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
#     description = models.TextField(blank=True, null=True)
#     image = models.ImageField( upload_to='ecom/',null=True, blank=True)
#     best_sellers = models.BooleanField(default=False,)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def get_price(self):
#         first_variant = self.variants.first()
#         return first_variant.price if first_variant else 0

#     def __str__(self):
#         return self.name
    
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base_slug = slugify(self.name)
#             slug = base_slug
#             counter = 1
#             while Product.objects.filter(slug=slug).exists():
#                 slug = f"{base_slug}-{counter}"
#                 counter += 1
#             self.slug = slug
#         super().save(*args, **kwargs)
    
#     def get_absolute_url(self):
#         return reverse("productdet", kwargs={
#             'slug':self.slug
#         })
#     def get_add_to_cart_url(self):
#         return reverse("add_to", kwargs={
#             'slug':self.slug
#         })
#     def get_add(self):
#         return reverse("add", kwargs={
#             'slug':self.slug
#         })

#     def get_remove(self):
#         return reverse("remove_from", kwargs={
#             'slug':self.slug
#         })

#     def get_remove_from_cart_url(self):
#         return reverse("remove_from", kwargs={
#             'slug':self.slug
#         })



# class ProductVariant(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
#     # color = models.ForeignKey(Color, on_delete=models.CASCADE,null=True, blank=True)
#     size = models.ForeignKey(Size, on_delete=models.CASCADE)
#     price = models.FloatField()
#     discount_price= models.FloatField(null=True, blank=True)
#     quantity = models.PositiveIntegerField(default=0)

#     class Meta:
#         unique_together = ('product', 'size')

#     def __str__(self):
#         return f"{self.product.name} - {self.size.name} ({self.quantity} pcs)"

# class Cart(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True, blank=True)
#     session_key = models.CharField(max_length=40, null=True, blank=True) 
#     size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)  # 👈 added
#     quantity = models.IntegerField(default=1,validators=[MinValueValidator(0)])
#     ordered = models.BooleanField(default=False)


#     @property
#     def variant(self):
#         return ProductVariant.objects.get(product=self.product, size=self.size)

#     @property
#     def price(self):
#         return self.variant.price

    
#     def __str__(self):
#         return f"{self.product.name} - {self.size.name} ({self.quantity} pcs)"




# class Address(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True, blank=True)

#     session_key = models.CharField(max_length=40, null=True, blank=True) 

#     first_name = models.CharField(max_length=100,blank=True, null=True)
#     last_name = models.CharField(max_length=100,blank=True, null=True)
#     email = models.EmailField(blank=True, null=True)
#     street_address = models.CharField(max_length=100,blank=True, null=True)
#     apartment = models.CharField(max_length=100,blank=True, null=True)
#     city = models.CharField(max_length=100,blank=True, null=True)
#     state = models.CharField(max_length=100,blank=True, null=True)

#     country = models.CharField(max_length=100,blank=True, null=True)
#     phone_number = models.CharField(max_length=100,blank=True, null=True)
#     default = models.BooleanField(default=False)





# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,null=True, blank=True)
#     email = models.EmailField(blank=True, null=True)
#     ref_code = models.CharField(max_length=100)
#     cart = models.ManyToManyField(Cart)
#     session_key = models.CharField(max_length=40, null=True, blank=True) 
#     address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True) 
#     amount = models.FloatField(null=True, blank=True)
#     Paid = models.BooleanField(default=False)
#     ordered_date = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(default='shipping')
#     coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)



#     def get_total_amount(self):
#         """
#         Returns the total cost of all items in this order.
#         """
#         total = 0
#         for cart_item in self.cart.all():
#             total += cart_item.price * cart_item.quantity
#         return total

    
#     def get_absolute_urlss(self):
#         return reverse("orderdet", kwargs={"id": self.id})


