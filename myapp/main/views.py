# myapp/main/views.py

from django.shortcuts import render, redirect
# --- Add these imports for the API ---
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import json
from .models import LabResult  # <-- Import the new LabResult model
from django.conf import settings

import json
# --- This safely imports the 'requests' library ---
try:
    import requests
except ImportError:
    requests = None


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


@login_required
def ai_chat_api(request):
    # --- Check if the 'requests' library is installed ---
    if requests is None:
        error_message = "The 'requests' library is not installed on the server. Please run 'pip install requests' in your terminal and restart the server."
        return JsonResponse({'reply': error_message, 'error': True})
    # -----------------------------------------------------------

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')

        # --- AI LOGIC USING GEMINI API ---
        api_key = settings.GEMINI_API_KEY
        # CORRECTED: This now checks for the placeholder text, which is more reliable.
        if not api_key or 'YOUR_GEMINI_API_KEY_HERE' in api_key:
            return JsonResponse({'reply': "AI API key is not configured in settings.py."})

        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        # This prompt gives the AI its personality and instructions
        prompt = f"""
        You are "HAUspital AI", a friendly and helpful assistant for the HAUspital web platform.
        Your primary goal is to assist users. You must follow these rules:
        1.  If asked for medical advice or to diagnose symptoms, you MUST provide a disclaimer that you are an AI and not a medical professional, and that the user should consult a real doctor. You can then provide basic, safe, public-knowledge first aid suggestions.
        2.  If asked about the platform (e.g., "how to book an appointment"), guide them on how to use the website's features.
        3.  For general questions, be a helpful and concise assistant.

        User's question: "{user_message}"
        """

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(api_url, json=payload, timeout=15)  # Added a timeout

        # --- IMPROVED ERROR HANDLING ---
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'An unknown API error occurred.')
                return JsonResponse({'reply': f"Error from AI Service: {error_message}"})
            except json.JSONDecodeError:
                return JsonResponse({
                                        'reply': f"Error from AI Service: Received an invalid response (Status code: {response.status_code})."})

        result = response.json()

        # --- Safely access the response text ---
        if 'candidates' in result and result.get('candidates'):
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
        else:
            error_info = result.get('error', {}).get('message', 'The AI service returned an unexpected response.')
            ai_response = f"I'm sorry, I couldn't generate a response. Details: {error_info}"

        return JsonResponse({'reply': ai_response.strip()})

    except requests.exceptions.RequestException as e:
        # This will catch network errors (like no internet) or timeouts
        error_details = str(e)
        if e.response:
            try:
                error_details = e.response.json().get('error', {}).get('message', str(e))
            except json.JSONDecodeError:
                error_details = e.response.text
        return JsonResponse(
            {'reply': f"Sorry, there was an error connecting to the AI service: {error_details}", 'error': True})
    except Exception as e:
        # This will catch any other unexpected errors in the code
        return JsonResponse({'reply': f"An unexpected error occurred on the server: {str(e)}"}, status=500)

