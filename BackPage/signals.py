from django.db.models.signals import pre_save
from django.dispatch import receiver
from .utils import convert_to_webp
from artist.models import Artist, Music
from video.models import Video
from authsystem.models import User
from market.models import ProductImage, PropertyImage

@receiver(pre_save, sender=Artist)
@receiver(pre_save, sender=Music)
@receiver(pre_save, sender=Video)
@receiver(pre_save, sender=User)
@receiver(pre_save, sender=ProductImage)
@receiver(pre_save, sender=PropertyImage)
def auto_convert_images_to_webp(sender, instance, **kwargs):
    # List of image fields for each model
    model_image_fields = {
        Artist: ['image'],
        Music: ['image'],
        Video: ['thumbnail'],
        User: ['image'],
        ProductImage: ['image'],
        PropertyImage: ['image'],
    }
    
    fields = model_image_fields.get(sender)
    if not fields:
        return

    for field_name in fields:
        # Get the field file
        file_field = getattr(instance, field_name)
        
        # Check if file exists and is validated
        if not file_field:
            continue
            
        # Check if it's a new file or changed
        if instance.pk:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                old_file = getattr(old_instance, field_name)
                if old_file == file_field:
                    continue
            except sender.DoesNotExist:
                pass  # It's a new instance with a provided PK? unlikely but possible
        
        # Check if it's already webp? Maybe not needed as we want to enforce it.
        # But if the user uploads a webp, convert_to_webp handles it or we can skip.
        # The utility returns a ContentFile, we should just use it.
        
        new_image = convert_to_webp(file_field)
        if new_image:
            # We need to assign it back to the field. 
            # Note: getattr returns a FieldFile which behaves like a file.
            # We need to save the new content to the field.
            # But wait, pre_save instance modification is tricky with FileFields.
            # Assigning a ContentFile to a FileField works.
            setattr(instance, field_name, new_image)
            # Important: The filename is updated in the utility function return value.
