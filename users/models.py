# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    User profile model to store additional biography information and user role,
    linked one-to-one with Django's built-in User model.
    """
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'), # <-- ADDED THIS NEW ROLE
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Basic biography fields
    full_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

# Signal to create a Profile automatically when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal to save the Profile whenever the User object is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Appointment:
    pass


class Doctor:
    pass