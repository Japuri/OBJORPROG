# mywebsite/users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views # Import Django's built-in auth views
from . import views

urlpatterns = [
    # Custom registration view
    path('register/', views.register, name='register'),

    # Custom login view (we'll use our own to handle messages and redirects)
    path('login/', views.user_login, name='login'),

    # Custom logout view
    path('logout/', views.user_logout, name='logout'),

    # User Profile Dashboard
    path('profile/', views.profile_dashboard, name='profile_dashboard'),


    # Django's built-in password reset views (optional, but good to have)
    # path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]