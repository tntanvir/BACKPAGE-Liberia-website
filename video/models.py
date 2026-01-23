from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class VideoCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
class Video(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True)
    tag = models.CharField(choices=[('music_video', 'Music Video'), ('movie', 'Movie')])
    youtube_url = models.URLField(blank=True, null=True)
    menual_video = models.FileField(upload_to='videos/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at','-updated_at']

class Videoview(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)
    
