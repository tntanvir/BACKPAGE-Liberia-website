from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Video, VideoCategory, Videoview
# Register your models here.


@admin.register(Video)
class VideoAdmin(ModelAdmin):
    list_display = ('title', 'tag', 'category', 'youtube_url', 'menual_video', 'created_at', 'updated_at')

@admin.register(VideoCategory)
class VideoCategoryAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

@admin.register(Videoview)
class VideoviewAdmin(ModelAdmin):
    list_display = ('video', 'view_count')
