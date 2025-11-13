# signals.py
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Product
import cloudinary.uploader

# Delete image when the Product is deleted
@receiver(post_delete, sender=Product)
def delete_cloudinary_image(sender, instance, **kwargs):
    if instance.image and getattr(instance.image, 'public_id', None):
        try:
            cloudinary.uploader.destroy(instance.image.public_id, resource_type="image")
            print("Deleted Cloudinary image:", instance.image.public_id)
        except Exception as e:
            print("Error deleting Cloudinary image:", e)

# Delete old image when the Product.image is updated
@receiver(pre_save, sender=Product)
def delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if this is a new object

    try:
        old_instance = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image != new_image:
        if getattr(old_image, 'public_id', None):
            try:
                cloudinary.uploader.destroy(old_image.public_id, resource_type="image")
                print("Deleted old Cloudinary image:", old_image.public_id)
            except Exception as e:
                print("Error deleting old Cloudinary image:", e)
