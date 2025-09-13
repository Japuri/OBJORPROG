# myapp/main/forms.py

from django import forms
from .models import Doctor

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialty', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500'}),
            'specialty': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500'}),
            'department': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500'}),
        }