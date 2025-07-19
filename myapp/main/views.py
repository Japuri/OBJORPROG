# myapp/main/views.py

from django.shortcuts import render, redirect
# --- Add these imports for the API ---
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import json
from .models import LabResult  # <-- Import the new LabResult model


# --- Your Existing Views ---
def home(request):
    """
    Renders the main front page of the website.
    """
    return render(request, 'main/index.html')


def features_view(request):
    """
    Renders the features page of the website.
    """
    return render(request, 'main/features.html')


def about_view(request):
    """
    Renders the about us page of the website.
    """
    return render(request, 'main/about.html')


@login_required
def book_appointment_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospital_name = data.get('hospitalName')
            doctor_name = data.get('doctorName')
            appointment_date = data.get('date')
            appointment_time = data.get('time')
            patient = request.user

            # ... (Save to database logic would go here) ...

            subject = f'Your Appointment Confirmation at {hospital_name}'
            message = f"""
Dear {patient.username},

This email confirms your appointment at {hospital_name} with {doctor_name}.

Date: {appointment_date}
Time: {appointment_time}

Thank you for choosing HAUspital.
            """

            send_mail(
                subject,
                message,
                'noreply@hauspital.com',
                [patient.email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success', 'message': 'Appointment booked and email sent.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


# --- ADD THIS NEW FUNCTION FOR FILE UPLOADS ---
@login_required
def upload_lab_result(request):
    if request.method == 'POST':
        if 'document' not in request.FILES:
            return JsonResponse({'status': 'error', 'message': 'No document was uploaded.'}, status=400)

        document = request.FILES['document']
        description = request.POST.get('description', '')

        LabResult.objects.create(
            patient=request.user,
            document=document,
            description=description
        )

        return JsonResponse({'status': 'success', 'message': 'File uploaded successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def home(request):
    """
    Renders the main front page for patients and guests,
    or redirects admins and doctors to their dashboards.
    """
    # --- THIS IS THE CRITICAL LOGIC ---
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'admin':
            # If a logged-in admin tries to visit the home page,
            # send them to the admin dashboard instead.
            return redirect('admin_dashboard')
        elif request.user.profile.role == 'doctor':
            # Do the same for doctors.
            return redirect('doctor_dashboard')
    # --- END OF LOGIC ---

    # Patients and non-logged-in users will see the regular home page as normal.
    # ... (the rest of your home view logic) ...
    return render(request, 'main/index.html')

# myapp/main/views.py

# ... (keep all your other views like home, book_appointment_api, etc.)

# --- ADD THIS NEW VIEW AT THE BOTTOM ---
@login_required
def lab_results_view(request):
    # Get all lab results belonging to the currently logged-in user
    user_results = LabResult.objects.filter(patient=request.user).order_by('-uploaded_at')

    context = {
        'user_lab_results': user_results
    }
    return render(request, 'main/lab_results.html', context)


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
