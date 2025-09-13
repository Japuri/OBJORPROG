from django.contrib import admin

# Register your models here.
# users/admin.py
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)