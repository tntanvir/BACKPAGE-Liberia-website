from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Product, ProductCategory ,Property

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name','user',  'brand', 'category', 'price', 'status', 'stock', 'created_at', 'updated_at')
    list_filter = ('status', 'stock')
    search_fields = ('name', 'brand', 'category__name')
    ordering = ('-created_at',)

@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

@admin.register(Property)
class PropertyAdmin(ModelAdmin):
    list_display = ('name', 'location', 'price', 'size', 'bed', 'bath', 'capacity', 'created_at', 'updated_at')
    list_filter = ('location', 'bed', 'bath')
    search_fields = ('name', 'location')
    ordering = ('-created_at',)