from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Artist, Music, Like, Dislike, Comment, Listen, Download, Category

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ('name', 'artist_type', 'bio', 'location', 'total_music', 'created_at')
    list_filter = ('artist_type', 'location')
    search_fields = ('name', 'bio', 'location')
    ordering = ('-created_at',)

    def total_music(self, obj):
        return obj.music_set.count()
    total_music.short_description = 'Total Music'

@admin.register(Music)
class MusicAdmin(ModelAdmin):
    list_display = ('title', 'artist', 'music_type', 'total_listens', 'total_downloads', 'created_at')
    list_filter = ('artist', 'music_type')
    search_fields = ('title', 'artist__name')
    ordering = ('-created_at',)

# ... (comments commented out in original)

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('-created_at',)