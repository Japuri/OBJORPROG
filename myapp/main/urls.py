# myapp/main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('features/', views.features_view, name='features'),
    path('about/', views.about_view, name='about'),
    path('api/book-appointment/', views.book_appointment_api, name='book_appointment_api'),

    # --- ADD THIS NEW URL PATTERN ---
    path('api/upload-result/', views.upload_lab_result, name='upload_lab_result_api'),

    path('lab-results/', views.lab_results_view, name='lab_results'),
]
