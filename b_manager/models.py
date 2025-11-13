from django.db import models
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date
from django.contrib.auth.models import User 
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import secrets
from storages.backends.s3boto3 import S3Boto3Storage

from django.urls import reverse



# Function to dynamically generate upload path for client files
def client_upload_to(instance, filename, folder_name):
    """
    Dynamically generate upload path for a Client's files.
    e.g., logo → 'clients/<client_name>/logo/<filename>'
          business_picture → 'clients/<client_name>/business_picture/<filename>'
    """
    client_name = instance.name or "unknown_client"
    client_name = slugify(client_name)  # make it URL-safe
    return f"clients/{client_name}/{folder_name}/{filename}"

def logo_upload_to(instance, filename):
    return client_upload_to(instance, filename, 'logo')

def business_picture_upload_to(instance, filename):
    return client_upload_to(instance, filename, 'business_picture')













class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=80, unique=True)
    plan_code = models.CharField(max_length=80, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_days = models.IntegerField(default=30)
    description = models.TextField(blank=True)
    can_use_custom_domain = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    cancelled_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.name

class Job(models.Model):
    name = models.CharField(blank=True, null=True)
    svg_url = models.CharField(max_length=200, blank=True, null=True, help_text="Live preview or demo link")
    det = models.CharField( blank=True, null=True)

    def __str__(self):
        return self.name



class WebsiteTemplate(models.Model):
    TEMPLATE_CATEGORIES = [
        ('Store', 'Store '),
        ('Restaurant', 'Restaurant'),
        ('Freelancer', 'Portfolio and Freelancer'),
        ('Photo Artist', 'Photo Artist'),
        ('Influencers', 'Content creator and Marketers '),
        ('Company', 'Company'),
        ('Blogger', '	Blog'),
        ('Food Vendor', 'Food Vendor'),
    ]

    PLAN_LEVELS = [
        ('free', 'Free Plan'),
        ('basic', 'Basic Plan'),
        ('premium', 'Premium Plan'),
    ]

    name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    slug = models.SlugField(unique=True,  blank=True, null=True)
    category = models.CharField(max_length=100, choices=TEMPLATE_CATEGORIES, blank=True, null=True)
    description = models.TextField( blank=True, null=True)
    thumbnail = models.ImageField(upload_to='template_thumbnails/', blank=True, null=True)
    preview_url = models.URLField(blank=True, null=True, help_text="Live preview or demo link")
    min_plan = models.CharField(
        max_length=20,
        choices=PLAN_LEVELS,
        default='free',
        help_text="Minimum subscription plan required to use this template.", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_min_plan_display()})"
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while WebsiteTemplate.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("customers:websitedet", kwargs={
            'slug':self.slug
        })




class Client(TenantMixin):
# TenantMixin fields: schema_name, domain_url etc are handled by django-tenants
    name = models.CharField(max_length=120,null=True, blank=True)
    business_name = models.CharField(max_length=100,null=True, blank=True, unique=True)
    urlconf = models.CharField(max_length=255, default='ecom.urls')
    Tagline = models.CharField(max_length=120,null=True, blank=True, unique=True)
    business_description = models.CharField(max_length=500,null=True, blank=True)
    street_address = models.CharField(max_length=25,null=True, blank=True)
    apartment_address = models.CharField(max_length=250,null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    # country = CountryField(multiple=False)
    zip = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)  
    bank = models.CharField(max_length=100, blank=True, null=True)
    account_no = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    # logo = models.ImageField(storage=S3Boto3Storage(),upload_to='logo/', null=True, blank=True)
    # logo = models.ImageField( upload_to='logo/', null=True, blank=True)
    # business_picture = models.ImageField( upload_to='buinesspics/', null=True, blank=True)
    # phone_number = PhoneNumberField(region="NG",null=True, blank=True)
    phone_number = models.CharField(max_length=40,null=True, blank=True)
    account_number = models.IntegerField(null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    plan = models.ForeignKey(SubscriptionPlan, null=True, blank=True, on_delete=models.SET_NULL)
    template_type = models.ForeignKey(WebsiteTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    job_type = models.ForeignKey(Job, null=True, blank=True, on_delete=models.SET_NULL)
    trial_ends_on = models.DateField(null=True, blank=True)
    has_used_trial = models.BooleanField(default=False)
    paid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    live = models.BooleanField(default=False)


    cloud_name = models.CharField(max_length=100, blank=True, null=True)
    api_key = models.CharField(max_length=100, blank=True, null=True)
    api_secret = models.CharField(max_length=100, blank=True, null=True)
    flutterwave_subaccount_id = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(
        upload_to=logo_upload_to,
        null=True, blank=True
    )

    business_picture = models.ImageField(
        upload_to=business_picture_upload_to,
        null=True, blank=True
    )



    auto_create_schema = True
    auto_drop_schema = True




    def on_trial(self):
        """Check if tenant is still within the trial period"""
        return self.trial_ends_on and self.trial_ends_on >= date.today()

    def subscription_active(self):
        """Check if paid subscription is still valid"""
        return self.paid_until and self.paid_until >= date.today()

    def update_status(self):
        """Automatically deactivate tenants when trial/subscription expires"""
        if self.on_trial() or self.subscription_active():
            if not self.is_active:
                self.is_active = True
                self.save(update_fields=['is_active'])
        else:
            if self.is_active:
                self.is_active = False
                self.save(update_fields=['is_active'])

    def is_valid(self):
        """Used for logic checks"""
        return self.is_active and (self.on_trial() or self.subscription_active())

    def days_left(self):
        """Return number of days left in trial or paid plan"""
        if self.on_trial():
            return (self.trial_ends_on - date.today()).days
        elif self.subscription_active():
            return (self.paid_until - date.today()).days
        return 0

    def __str__(self):
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    pass

class User(AbstractUser):
    tenant = models.ForeignKey(
        'Client', on_delete=models.CASCADE, null=True, blank=True
    )
class PaystackEventLog(models.Model):
    event = models.CharField(max_length=100)
    received_at = models.DateTimeField(auto_now_add=True)
    raw_data = models.JSONField()



class TenantAPIKey(models.Model):
    tenant = models.OneToOneField(Client, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=128, unique=True, default=secrets.token_urlsafe)
    created_at = models.DateTimeField(auto_now_add=True)

    def regenerate_key(self):
        self.api_key = secrets.token_urlsafe()
        self.save()


class ChatHistory(models.Model):
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE)
    user_number = models.CharField(max_length=50)
    role = models.CharField(max_length=20)  # "user" or "assistant"
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)