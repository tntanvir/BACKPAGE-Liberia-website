from django.contrib import admin
from .models import Ads, AdsPage
from unfold.admin import ModelAdmin
# Register your models here.
# admin.site.register(Ads)
# admin.site.register(AdsPage)
@admin.register(AdsPage)
class AdsPageAdmin(ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_display_links = ('id', 'created_at', 'updated_at')
    list_editable = ('name',)
    list_per_page = 25
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('-created_at',)

@admin.register(Ads)
class AdsAdmin(ModelAdmin):
    list_display = ('id', 'page', 'image', 'link', 'created_at', 'updated_at')
    list_display_links = ('id', 'created_at', 'updated_at')
    list_editable = ('page', 'image', 'link')
    list_per_page = 25
    search_fields = ('page__name', 'link')
    list_filter = ('page', 'link')
    ordering = ('-created_at',)