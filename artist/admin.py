from django.contrib import admin
from .models import Artist, Music , Like, Dislike, Comment, Listen, Download

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_type', 'bio', 'location', 'total_music', 'created_at')
    list_filter = ('artist_type', 'location')
    search_fields = ('name', 'bio', 'location')
    ordering = ('-created_at',)

    def total_music(self, obj):
        return obj.music_set.count()
    total_music.short_description = 'Total Music'

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'music_type', 'total_listens', 'total_downloads', 'created_at')
    list_filter = ('artist', 'music_type')
    search_fields = ('title', 'artist__name')
    ordering = ('-created_at',)

# @admin.register(Like)
# class LikeAdmin(admin.ModelAdmin):
#     list_display = ('user', 'music', 'created_at')
#     list_filter = ('user', 'music')
#     search_fields = ('user__username', 'music__title')
#     ordering = ('-created_at',)

# @admin.register(Dislike)
# class DislikeAdmin(admin.ModelAdmin):
#     list_display = ('user', 'music', 'created_at')
#     list_filter = ('user', 'music')
#     search_fields = ('user__username', 'music__title')
#     ordering = ('-created_at',)

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'music', 'comment', 'created_at')
#     list_filter = ('user', 'music')
#     search_fields = ('user__username', 'music__title')
#     ordering = ('-created_at',)

# @admin.register(Listen)
# class ListenAdmin(admin.ModelAdmin):
#     list_display = ('user', 'music', 'created_at')
#     list_filter = ('user', 'music')
#     search_fields = ('user__username', 'music__title')
#     ordering = ('-created_at',)

# @admin.register(Download)
# class DownloadAdmin(admin.ModelAdmin):
#     list_display = ('user', 'music', 'created_at')
#     list_filter = ('user', 'music')
#     search_fields = ('user__username', 'music__title')
#     ordering = ('-created_at',)