from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile


class RegeisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['PRFfirst_name','PRFlast_name','PRFphone_number','PRFaddress','PRFcity','PRFcountry','PRFpostal_code','PRFprofile_image','PRFdate_of_birth']
    
    
