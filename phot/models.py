from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.

from django.utils.text import slugify 


class Photo(models.Model):
    title= models.CharField(max_length=1000)
    description = models.TextField()
    slug = models.SlugField()

    image = CloudinaryField(folder='photo')
    featured = models.BooleanField(default=False,)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Photo.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)




class Bookings(models.Model):
    full_name = models.CharField(max_length=1000)
    email = models.EmailField()
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Myself(models.Model):
    name = models.TextField()
    image = CloudinaryField(folder='photos', help_text="A picture of yourself")
    image_tool = CloudinaryField(folder='photos',help_text="A picture of your camera or phone you use to take pictures")
    my_story = models.TextField()
    expertise =  models.TextField()
    image_demo = CloudinaryField(folder='photos', help_text="One of your favorite professional picture")


class Service_Photo(models.Model):
    name = models.CharField()
    description = models.TextField(help_text="list of photos youll take and edit for the client")
    amount = models.FloatField()






class WebsiteVisitertgerg(models.Model):
    path = models.CharField(max_length=255)  # Optional: track which page
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    referrer = models.CharField(max_length=255, blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} visited {self.path} at {self.timestamp}"