# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail

from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import Profile
from main.models import LabResult, Appointment, Doctor, Admission
from main.models import Admission


def register(request):
    """
    Handles user registration.
    Displays a registration form and creates a new user and profile upon valid submission.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            return redirect('home')  # Redirect to the main home page after registration
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """
    Handles user login with role-based redirection.
    """
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')

                # --- ROLE-BASED REDIRECTION LOGIC ---
                if hasattr(user, 'profile'):
                    if user.profile.role == 'admin':
                        return redirect('admin_dashboard')
                    elif user.profile.role == 'doctor':
                        return redirect('doctor_dashboard')
                    else:  # Patient
                        return redirect('home')  # Patients go to the main home page
                else:
                    # Fallback for safety (e.g., superuser without a profile)
                    return redirect('home')
                # --- END OF LOGIC ---

            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def profile_dashboard(request):
    """
    Displays the user's profile dashboard.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # This signal should handle profile creation, but this is a safe fallback.
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {
        'form': form
    }
    return render(request, 'users/profile_dashboard.html', context)


@login_required
def user_logout(request):
    """
    Logs out the current user.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def admin_dashboard_view(request):
    """
    Displays the admin dashboard with real data from the database.
    """
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    patient_count = Profile.objects.filter(role='patient').count()
    doctor_count = Profile.objects.filter(role='doctor').count()
    appointments_today_count = Appointment.objects.filter(appointment_date=timezone.now().date()).count()

    context = {
        'patient_count': patient_count,
        'doctor_count': doctor_count,
        'appointments_today_count': appointments_today_count,
    }
    return render(request, 'users/admin_dashboard.html', context)


@login_required
def doctor_dashboard_view(request):
    """
    Displays the doctor dashboard with a list of lab results to be reviewed.
    """
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'doctor'):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    pending_results = LabResult.objects.filter(status='Pending Review').order_by('-uploaded_at')

    context = {
        'pending_results': pending_results
    }
    return render(request, 'users/doctor_dashboard.html', context)


@login_required
def update_lab_result_status(request, result_id):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'doctor'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    lab_result = get_object_or_404(LabResult, id=result_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Reviewed', 'Action Required']:
            lab_result.status = new_status
            lab_result.save()
            messages.success(request,
                             f"Status for '{lab_result.description or lab_result.document.name}' updated successfully.")
        else:
            messages.error(request, "Invalid status selected.")

    return redirect('doctor_dashboard')


@login_required
def manage_patients_view(request):
    # Security check to ensure only admins can access this page
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    # Fetch all profiles with the role of 'patient'
    patient_profiles = Profile.objects.filter(role='patient').order_by('user__username')

    context = {
        'patients': patient_profiles
    }
    return render(request, 'users/manage_patients.html', context)


# --- ADD THIS NEW VIEW FOR ADMITTING PATIENTS ---
@login_required
def admit_patient_view(request, patient_id):
    # Security check for admin role
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    patient_to_admit = get_object_or_404(User, id=patient_id)
    doctors = Doctor.objects.all()  # Get all doctors for the dropdown

    if request.method == 'POST':
        admission_type = request.POST.get('admission_type')
        doctor_id = request.POST.get('doctor_id')

        # Validation
        if not admission_type or not doctor_id:
            messages.error(request, 'Please select an admission type and a doctor.')
        else:
            assigned_doctor = get_object_or_404(Doctor, id=doctor_id)

            # Create the Admission record in the database
            Admission.objects.create(
                patient=patient_to_admit,
                admission_type=admission_type,
                assigned_doctor=assigned_doctor,
                status='Admitted'
            )

            # --- Send the Email Notification ---
            subject = f'You have been admitted to HAUspital'
            message = f"""
Dear {patient_to_admit.username},

You have been successfully admitted to HAUspital.

Admission Type: {admission_type}
Assigned Doctor: {assigned_doctor.name} ({assigned_doctor.specialty})
Department: {assigned_doctor.department}

Please follow any further instructions from our staff.

Thank you,
HAUspital Administration
            """
            send_mail(
                subject,
                message,
                'noreply@hauspital.com',
                [patient_to_admit.email],
                fail_silently=False,
            )

            messages.success(request, f'{patient_to_admit.username} has been admitted and notified via email.')
            return redirect('manage_patients')

    context = {
        'patient': patient_to_admit,
        'doctors': doctors
    }
    return render(request, 'users/admit_patient.html', context)


@login_required
def delete_patient_view(request, patient_id):
    # Security check to ensure only admins can perform this action
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    # Find the user object to be deleted
    patient_to_delete = get_object_or_404(User, id=patient_id)

    if request.method == 'POST':
        try:
            # The associated Profile will be deleted automatically because of the
            # on_delete=models.CASCADE setting in your Profile model.
            patient_username = patient_to_delete.username
            patient_to_delete.delete()
            messages.success(request, f'Patient "{patient_username}" has been successfully deleted.')
        except Exception as e:
            messages.error(request, f'An error occurred while trying to delete the patient: {e}')

        return redirect('manage_patients')

    # If the request is not POST, just redirect back.
    # A more advanced version might show a confirmation page.
    return redirect('manage_patients')


@login_required
def current_admissions_view(request):
    # Security check to ensure only admins can access this page
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    # Fetch all admission records where the status is 'Admitted'
    current_admissions = Admission.objects.filter(status='Admitted').order_by('-admission_date')

    context = {
        'admissions': current_admissions
    }
    return render(request, 'users/current_admissions.html', context)


@login_required
def discharge_patient_view(request, admission_id):
    # Security check to ensure only admins can perform this action
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    # Find the specific admission record to be updated
    admission_record = get_object_or_404(Admission, id=admission_id)

    if request.method == 'POST':
        try:
            # Update the status and save the record
            admission_record.status = 'Discharged'
            admission_record.save()
            messages.success(request,
                             f'Patient "{admission_record.patient.username}" has been successfully discharged.')
        except Exception as e:
            messages.error(request, f'An error occurred while trying to discharge the patient: {e}')

        return redirect('current_admissions')

    # If the request is not POST, just redirect back.
    return redirect('current_admissions')


@login_required
def transfer_patient_view(request, admission_id):
    # Security check for admin role
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    admission_record = get_object_or_404(Admission, id=admission_id)
    # Exclude the currently assigned doctor from the list of choices
    doctors = Doctor.objects.exclude(id=admission_record.assigned_doctor.id)

    if request.method == 'POST':
        new_doctor_id = request.POST.get('doctor_id')

        if not new_doctor_id:
            messages.error(request, 'Please select a new doctor to transfer the patient to.')
        else:
            new_doctor = get_object_or_404(Doctor, id=new_doctor_id)

            # Update the assigned doctor on the admission record
            admission_record.assigned_doctor = new_doctor
            admission_record.save()

            # (Optional) Here you could add another email notification to the patient
            # about the change in their assigned doctor.

            messages.success(request,
                             f'Patient "{admission_record.patient.username}" has been successfully transferred to Dr. {new_doctor.name}.')
            return redirect('current_admissions')

    context = {
        'admission': admission_record,
        'doctors': doctors
    }
    return render(request, 'users/transfer_patient.html', context)