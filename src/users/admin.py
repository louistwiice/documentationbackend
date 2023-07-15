from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.models import Permission



class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_active']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Permission)
