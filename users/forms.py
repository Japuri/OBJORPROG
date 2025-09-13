# mywebsite/users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

class UserRegisterForm(UserCreationForm):
    """
    Form for user registration, extending Django's built-in UserCreationForm.
    Includes additional fields for the user's profile.
    """
    email = forms.EmailField(required=True, label="Email Address",
                             widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'}))

    full_name = forms.CharField(max_length=100, required=True, label="Full Name",
                                widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'}), required=False, label="Date of Birth")
    address = forms.CharField(max_length=255, required=False, label="Address",
                              widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'}))
    phone_number = forms.CharField(max_length=20, required=False, label="Phone Number",
                                   widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'}), required=False, label="About Me")


    class Meta(UserCreationForm.Meta):
        model = User
        # Include all default fields from UserCreationForm, then add our custom ones.
        # This implicitly includes 'password' and 'password2' from the parent.
        fields = UserCreationForm.Meta.fields + ('email', 'full_name', 'date_of_birth', 'address', 'phone_number', 'bio',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('email', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('password', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('password2', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('full_name', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('date_of_birth', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('address', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('phone_number', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('bio', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Submit('submit', 'Sign Up', css_class='w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition duration-300 ease-in-out shadow-md transform hover:scale-105')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data.get('full_name')
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.address = self.cleaned_data.get('address')
            profile.phone_number = self.cleaned_data.get('phone_number')
            profile.bio = self.cleaned_data.get('bio')
            profile.save()
        return user

class UserLoginForm(AuthenticationForm):
    """
    Form for user login, extending Django's built-in AuthenticationForm.
    """
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('password', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Submit('submit', 'Log In', css_class='w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition duration-300 ease-in-out shadow-md transform hover:scale-105')
        )

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating the user's profile information.
    """
    class Meta:
        model = Profile
        fields = ['full_name', 'date_of_birth', 'address', 'phone_number', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('full_name', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('date_of_birth', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('address', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('phone_number', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Field('bio', css_class='w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-200'),
            Submit('submit', 'Update Profile', css_class='w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition duration-300 ease-in-out shadow-md transform hover:scale-105')
        )
