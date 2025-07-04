# mywebsite/mywebsite/urls.py

from django.contrib import admin
from django.urls import path, include # Import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), # Include your app's URLs at the root
]