from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.
from django.conf import settings

from django.utils.text import slugify 

# Create your models here.


class Comm(models.Model):
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Blog(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = CloudinaryField(folder='thub/',null=True, blank=True)
    cataegory = models.CharField(max_length=100,null=True, blank=True)
    featured = models.BooleanField(default=False)
    comment = models.ManyToManyField(Comm, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    # def get_absolute_url(self):
    #     return reverse("productdet", kwargs={
    #         'slug':self.slug
    #     })

   

class Abbb(models.Model):
    my_story = models.TextField()
    our_mission = models.TextField()
    why = models.TextField()

class Msg(models.Model):
    name = models.CharField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Sub(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email





class WebsiteViwreger(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,null=True, blank=True)
    path = models.CharField(max_length=255)  # Optional: track which page
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    referrer = models.CharField(max_length=255, blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} visited {self.path} at {self.timestamp}"