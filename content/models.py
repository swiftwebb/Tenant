from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.


from django.utils.text import slugify 
class Categorysss(models.Model):
    name = models.CharField()
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Categorysss.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)



class Socails(models.Model):
    name = models.CharField()
    like = models.CharField(blank=True)
    comment = models.CharField(blank=True)
    views = models.CharField(blank=True)
    thumbnail = CloudinaryField(folder='tunb/',)
    link = models.URLField(help_text="paste the link of the video")
    category = models.ForeignKey(Categorysss, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class Campagin(models.Model):
    Title = models.CharField()
    social = models.ForeignKey(Socails, on_delete=models.CASCADE)
    problem=  models.TextField(help_text="explain the problems the clients faced")
    overview=  models.TextField(help_text="share the overview of what you did")

    solution=  models.TextField(help_text="Share the solutions that you took")
    result =  models.TextField(help_text="Share the result")
    created_at = models.DateTimeField(auto_now_add=True)


class Service(models.Model):
    name = models.CharField()
    description = models.TextField(help_text="list of what will you post either one video or multiple video and the socail media you'll post it")
    amount = models.FloatField(help_text=" the amount you'll charge")




class Mess(models.Model):
    name = models.CharField()
    email = models.EmailField()
    messages = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Home(models.Model):
    title = models.CharField()
    description = models.TextField()
    image = CloudinaryField(folder='homie/',)
    

class About(models.Model):
    title = models.CharField()
    description = models.TextField()
    image =CloudinaryField(folder='about/',)
    


class WebsiteVisiterggssfe(models.Model):
    path = models.CharField(max_length=255)  # Optional: track which page
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    referrer = models.CharField(max_length=255, blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} visited {self.path} at {self.timestamp}"