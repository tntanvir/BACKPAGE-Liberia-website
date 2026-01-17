from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'status', 'stock', 'created_at', 'updated_at')
    list_filter = ('status', 'stock')
    search_fields = ('name', 'brand', 'category')
    ordering = ('-created_at',)