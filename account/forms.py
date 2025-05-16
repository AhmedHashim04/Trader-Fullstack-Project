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
    first_name = forms.CharField(max_length=150,required=False)
    last_name = forms.CharField(max_length=150,required=False)
    phone_number = forms.CharField(
        max_length=11,
        min_length=11,
        validators=[
            RegexValidator(
                regex=r'^(010|011|012|015)\d{8}$',
                message="Enter a valid Egyptian phone number starting with 010, 011, 012, or 015."
            )
        ],
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    class Meta:
        model = Profile
        fields = [ 
        'first_name', 'last_name', 'phone_number', 'address', 'city', 'country', 'postal_code', 'profile_image', 'date_of_birth',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
            profile.save()
        return profile
    
