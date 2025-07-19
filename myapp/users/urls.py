# users/urls.py

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

    # --- ADD THESE NEW URLS FOR THE DASHBOARDS ---
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),

    path('lab-result/<int:result_id>/update-status/', views.update_lab_result_status, name='update_lab_result_status'),

    path('manage-patients/', views.manage_patients_view, name='manage_patients'),

    path('admit-patient/<int:patient_id>/', views.admit_patient_view, name='admit_patient'),

    path('delete-patient/<int:patient_id>/', views.delete_patient_view, name='delete_patient'),

    path('current-admissions/', views.current_admissions_view, name='current_admissions'),

    path('discharge-patient/<int:admission_id>/', views.discharge_patient_view, name='discharge_patient'),

    path('discharge-patient/<int:admission_id>/', views.discharge_patient_view, name='discharge_patient'),

    # --- ADD THIS NEW URL FOR THE TRANSFER ACTION ---
    path('transfer-patient/<int:admission_id>/', views.transfer_patient_view, name='transfer_patient'),path('discharge-patient/<int:admission_id>/', views.discharge_patient_view, name='discharge_patient'),

    # --- ADD THIS NEW URL FOR THE TRANSFER ACTION ---
    path('transfer-patient/<int:admission_id>/', views.transfer_patient_view, name='transfer_patient'),
    # ---------------------------------------------

    # Django's built-in password reset views (optional, but good to have)
    # path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
