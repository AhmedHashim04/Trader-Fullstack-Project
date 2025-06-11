from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from django.core.validators import RegexValidator

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class UpdateProfileForm(forms.ModelForm):
        first_name = forms.CharField(max_length=150,required=False,label="First Name")
        last_name = forms.CharField(max_length=150,required=False,label="Last Name")
        phone_number = forms.CharField(max_length=11,min_length=11,required=False,validators=[RegexValidator(regex=r'^(010|011|012|015)\d{8}$',message="Enter a valid Egyptian phone number starting with 010, 011, 012, or 015.")],label="Phone Number")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._initialize_user_fields()
            self._initialize_profile_fields()

        def _initialize_user_fields(self):
            if self.instance and hasattr(self.instance, 'user') and self.instance.user:
                self.fields['first_name'].initial = self.instance.user.first_name
                self.fields['last_name'].initial = self.instance.user.last_name

        def _initialize_profile_fields(self):
            if self.instance and hasattr(self.instance, 'phone_number'):
                self.fields['phone_number'].initial = self.instance.phone_number
        class Meta:
            model = Profile
            fields = [
                'first_name', 'last_name', 'phone_number', 'address', 'city', 
                'country', 'postal_code', 'profile_image', 'date_of_birth']
            widgets = {
                'date_of_birth': forms.DateInput(attrs={'type': 'date'}), }

        def save(self, commit=True):
            profile = super().save(commit=False)
            self._update_user_fields()
            if commit:
                profile.user.save()
                profile.save()
            return profile
        
        def _update_user_fields(self):
            if self.cleaned_data.get('first_name') is not None:
                self.instance.user.first_name = self.cleaned_data['first_name']
            if self.cleaned_data.get('last_name') is not None:
                self.instance.user.last_name = self.cleaned_data['last_name']
