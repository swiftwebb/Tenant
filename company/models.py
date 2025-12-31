from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.
from django.conf import settings

from django.utils.text import slugify 




class Ideal(models.Model):
    overview = models.TextField()
    description =  models.TextField()
    image = CloudinaryField(folder='lead/',null=True, blank=True)

class Serv(models.Model):
    title = models.CharField()
    overview = models.TextField()
    premium = models.BooleanField(default=False)

class Leaders(models.Model):
    title =models.CharField()
    name = models.CharField()
    image = CloudinaryField(folder='lead/',null=True, blank=True)


class Abut(models.Model):
    image = CloudinaryField(folder='lead/',null=True, blank=True)
    title = models.CharField(default="About Company")

    description = models.TextField()




class Imes(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.email}"








class WebsiteVisitgthberbr(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,null=True, blank=True)
    path = models.CharField(max_length=255)  # Optional: track which page
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    referrer = models.CharField(max_length=255, blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} visited {self.path} at {self.timestamp}"