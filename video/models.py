from django.db import models

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    youtube_url = models.URLField(blank=True, null=True)
    menual_video = models.FileField(upload_to='videos/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)