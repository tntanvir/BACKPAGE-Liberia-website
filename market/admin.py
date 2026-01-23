from django.contrib import admin
from .models import Product, ProductCategory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'status', 'stock', 'created_at', 'updated_at')
    list_filter = ('status', 'stock')
    search_fields = ('name', 'brand', 'category__name')
    ordering = ('-created_at',)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')