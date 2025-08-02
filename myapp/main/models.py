# myapp/main/models.py

from django.db import models
from django.contrib.auth.models import User  # Use Django's built-in User model


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"


class Admission(models.Model):
    ADMISSION_TYPES = [
        ('Emergency', 'Emergency'),
        ('Outpatient', 'Outpatient'),
        ('Inpatient', 'Inpatient'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    admission_type = models.CharField(max_length=20, choices=ADMISSION_TYPES)
    admission_date = models.DateTimeField(auto_now_add=True)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='Admitted')

    def __str__(self):
        return f"{self.patient.username} admitted on {self.admission_date.strftime('%Y-%m-%d')}"


class LabResult(models.Model):
    """
    Represents a lab result document uploaded by a user.
    """
    STATUS_CHOICES = (
        ('Pending Review', 'Pending Review'),
        ('Reviewed', 'Reviewed'),
        ('Action Required', 'Action Required'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_results')
    document = models.FileField(upload_to='lab_results/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Review')

    def __str__(self):
        # This will return the name of the file, e.g., "blood_test_results.pdf"
        return self.document.name.split('/')[-1]


class Appointment(models.Model):
    """
    Represents an appointment booked by a patient with a doctor.
    """
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=255)
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='Booked')
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.patient.username} with {self.doctor.name} on {self.appointment_date}"

