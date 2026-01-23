from django.contrib import admin
from .models import Video, VideoCategory, Videoview
# Register your models here.


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'category', 'youtube_url', 'menual_video', 'created_at', 'updated_at')

@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

@admin.register(Videoview)
class VideoviewAdmin(admin.ModelAdmin):
    list_display = ('video', 'view_count')
