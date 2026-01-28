from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Product, ProductCategory ,Property, ProductImage
from django.utils.html import format_html

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("image_preview",)
    fields = ("image", "image_preview")  # order matters

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:250px; width:auto; border-radius:6px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name','user', 'brand', 'category', 'price', 'status', 'stock', 'created_at', 'updated_at')
    list_filter = ('status', 'stock')
    search_fields = ('name', 'brand', 'category__name')
    ordering = ('-created_at',)
    inlines = [ProductImageInline]

@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

@admin.register(Property)
class PropertyAdmin(ModelAdmin):
    list_display = ('name', 'location', 'price', 'size', 'bed', 'bath', 'capacity', 'created_at', 'updated_at')
    list_filter = ('location', 'bed', 'bath')
    search_fields = ('name', 'location')
    ordering = ('-created_at',)