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
    name = models.CharField(blank=True)
    like = models.CharField(blank=True)
    comment = models.CharField(blank=True)
    views = models.CharField(blank=True)
    thumbnail = CloudinaryField(folder='tunb/', blank=True, null=True)
    link = models.URLField(blank=True)
    category = models.ForeignKey(Categorysss, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class Campagin(models.Model):
    Title = models.CharField(blank=True)
    social = models.ForeignKey(Socails, on_delete=models.CASCADE,null=True, blank=True)
    problem=  models.TextField(blank=True)
    overview=  models.TextField(max_length=150,blank=True)

    solution=  models.TextField(blank=True)
    result =  models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Service(models.Model):
    name = models.CharField(blank=True)
    description = models.TextField(blank=True, help_text="list what will post either one video or multiple video and the socail media")
    amount = models.FloatField(null=True, blank=True)




class Mess(models.Model):
    name = models.CharField(blank=True)
    email = models.EmailField(blank=True)
    messages = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Home(models.Model):
    title = models.CharField(blank=True)
    description = models.TextField(blank=True)
    image = CloudinaryField(folder='homie/', blank=True, null=True)
    

class About(models.Model):
    title = models.CharField(blank=True)
    description = models.TextField(blank=True)
    image =CloudinaryField(folder='about/', blank=True, null=True)
    

