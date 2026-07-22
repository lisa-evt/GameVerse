from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('gameVerse profile', {'fields': ('profile_picture', 'bio')}),
    )


admin.site.register(User, CustomUserAdmin)
