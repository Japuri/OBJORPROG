# mywebsite/mywebsite/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
     # <--- Include your users app URLs here
    # You can also include Django's default auth URLs if you prefer, but we're customizing
    # path('accounts/', include('django.contrib.auth.urls')),
]
