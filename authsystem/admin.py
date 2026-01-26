from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('email', 'name', 'is_verified')