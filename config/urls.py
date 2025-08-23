# mywebsite/mywebsite/urls.py

from django.contrib import admin
from django.urls import path, include

from django.contrib import admin
from django.urls import path, include # 1. Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')), # 2. Add this line to include your app's URLs
]