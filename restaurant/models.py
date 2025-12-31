from django.db import models
from cloudinary.models import CloudinaryField

from django.utils.text import slugify 
# Create your models here.



class Hom(models.Model):
    image = CloudinaryField(folder='restu/', blank=True, null=True)




class Catgg(models.Model):
    CATEGORY_CHOICES = [
        ("appetizers", "Appetizers"),
        ("main_courses", "Main Courses"),
        ("desserts", "Desserts"),
        ("cocktails", "Cocktails"),
        ("mocktails", "Mocktails"),
        ("sides", "Sides"),
        ("beverages", "Non-Alcoholic Beverages"),
        ("wine_beer", "Wine & Beer"),

    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    slug = models.SlugField(unique=True, blank=True)


       
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Catgg.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Menu(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True, blank=True)
    category = models.ForeignKey(Catgg, on_delete=models.CASCADE,null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image = CloudinaryField(folder='menu/', blank=True, null=True)





    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Menu.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)





class Bookdbdbd(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    guests = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"