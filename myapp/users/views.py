# mywebsite/users/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# No need for JsonResponse or json module imports for standard forms
# from django.http import JsonResponse
# import json

from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import Profile

def register(request):
    """
    Handles user registration.
    Displays a registration form and creates a new user and profile upon valid submission.
    Expects standard POST data and performs a redirect.
    """
    if request.method == 'POST':
        # Data comes directly from request.POST for standard form submission
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after successful registration
            login(request, user)
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            return redirect('profile_dashboard') # Redirect to profile dashboard
        else:
            # Add form errors to messages for display on the page
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()
    # Render the form template with errors if any
    return render(request, 'users/register.html', {'form': form, 'form_type': 'signup'})

def user_login(request):
    """
    Handles user login.
    Displays a login form and authenticates the user upon valid submission.
    Expects standard POST data and performs a redirect.
    """
    if request.method == 'POST':
        # Data comes directly from request.POST for standard form submission
        form = UserLoginForm(request, data=request.POST) # Pass request to AuthenticationForm
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password) # Pass request to authenticate
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('profile_dashboard') # Redirect to profile dashboard
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # Add form errors to messages for display on the page
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserLoginForm()
    # Render the form template with errors if any
    return render(request, 'users/login.html', {'form': form, 'form_type': 'login'})

@login_required
def profile_dashboard(request):
    """
    Displays the user's profile dashboard.
    Allows logged-in users to view and update their biography information.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        messages.info(request, "Your profile was just created. Please fill out your details.")

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile field '{field}': {error}")
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {
        'user': request.user,
        'profile': profile,
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


# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import Appointment, Doctor  # Assuming you have these models


@login_required  # Ensures only logged-in users can access this
def book_appointment_api(request):
    if request.method == 'POST':
        try:
            # 1. Get data from the frontend
            data = json.loads(request.body)
            doctor_id = data.get('doctorId')
            appointment_date = data.get('date')
            appointment_time = data.get('time')
            patient = request.user

            # 2. Save the appointment to your database
            # (This is a simplified example)
            doctor = Doctor.objects.get(id=doctor_id)
            new_appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status='Booked'
            )

            # 3. Send the confirmation email
            subject = 'Your Appointment Confirmation at HAUspital'
            message = f"""
Dear {patient.username},

This email confirms your appointment with {doctor.name}.

Date: {appointment_date}
Time: {appointment_time}

Thank you for choosing HAUspital.
            """
            send_mail(
                subject,
                message,
                'noreply@hauspital.com',  # From email
                [patient.email],  # To email (the user's registered email)
                fail_silently=False,
            )

            # 4. Send a success response back to the frontend
            return JsonResponse({'status': 'success', 'message': 'Appointment booked and email sent.'})

        except Exception as e:
            # If anything goes wrong, send an error response
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Handle non-POST requests
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)