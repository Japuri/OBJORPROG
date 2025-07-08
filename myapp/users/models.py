from django.db import models

# Create your models here.

# mywebsite/users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    User profile model to store additional biography information,
    linked one-to-one with Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Basic biography fields
    full_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # You can add more fields here as needed, e.g., profile_picture, gender, etc.

    def __str__(self):
        return f'{self.user.username} Profile'

# Signal to create a Profile automatically when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Profile object when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)

# Signal to save the Profile whenever the User object is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically saves the Profile object whenever the associated User is saved.
    """
    instance.profile.save()


class Appointment:
    pass


class Doctor:
    pass