import io
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

def convert_to_webp(image_field):
    """
    Converts a Django ImageField file to WebP format.
    """
    if not image_field:
        return None

    # Open the image using Pillow
    img = Image.open(image_field)
    
    # Convert to RGB if necessary (e.g., for PNG with transparency)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Save the image to a BytesIO object in WebP format
    buffer = io.BytesIO()
    img.save(buffer, format='WEBP', quality=80)
    buffer.seek(0)
    
    # Create a new Django ContentFile
    filename = os.path.splitext(image_field.name)[0] + '.webp'
    return ContentFile(buffer.read(), name=filename)
