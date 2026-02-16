from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from .models import Profile  # Optional, if Profile model exists

# Optional: If you have a Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend UserAdmin to include Profile inline
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

# Unregister the default User admin and register custom User admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# If you don't have a Profile model, you can leave accounts/admin.py empty or omit it:
# from django.contrib import admin