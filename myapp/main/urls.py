# mywebsite/main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('features/', views.features_view, name='features'),
    path('about/', views.about_view, name='about'), # NEW URL PATTERN
]