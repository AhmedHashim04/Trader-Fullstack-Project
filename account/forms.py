from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import Profile
from django.core.exceptions import ValidationError
import re
from django.utils import timezone

User = get_user_model()
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email'
        }),
        help_text=_("We'll never share your email with anyone else.")
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        labels = {
            'username': _('Username'),
        }
        help_texts = {
            'username': _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Choose a username'),
                'autocomplete': 'username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enhance password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Create a password'),
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm your password'),
            'autocomplete': 'new-password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email address is already in use."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError(_("Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."))
        return username


class UpdateProfileForm(forms.ModelForm):
    """
    Advanced profile update form with user and profile fields integration
    """
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("First Name"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your first name')
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Last Name"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your last name')
        })
    )
    
    phone_number = forms.CharField(
        max_length=11,
        min_length=11,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^(010|011|012|015)\d{8}$',
                message=_("Enter a valid Egyptian phone number starting with 010, 011, 012, or 015.")
            )
        ],
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('e.g. 01012345678')
        }),
        help_text=_("Enter your 11-digit Egyptian phone number starting with 010, 011, 012, or 015.")
    )

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'phone_number', 'address', 'city', 
            'country', 'postal_code', 'profile_image', 'date_of_birth'
        ]
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your address in Arabic')
            }),
            'city': forms.Select(attrs={
                'class': 'form-select'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your postal code')
            }),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': timezone.now().date().isoformat()
                },
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'address': _("Address"),
            'city': _("City"),
            'country': _("Country"),
            'postal_code': _("Postal Code"),
            'profile_image': _("Profile Image"),
            'date_of_birth': _("Date of Birth"),
        }
        help_texts = {
            'postal_code': _("Enter a valid Egyptian postal code (3-5 digits)"),
            'date_of_birth': _("Format: YYYY-MM-DD"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialize_user_fields()
        self._initialize_profile_fields()

    def _initialize_user_fields(self):
        """Initialize user-related fields from the associated User model"""
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def _initialize_profile_fields(self):
        """Initialize profile-specific fields"""
        if self.instance and hasattr(self.instance, 'phone_number'):
            self.fields['phone_number'].initial = self.instance.phone_number

    def clean_phone_number(self):
        """Additional validation for phone number"""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise ValidationError(_("Phone number must contain only digits."))
        return phone_number

    def clean_date_of_birth(self):
        """Validate date of birth to be in the past"""
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth and date_of_birth > timezone.now().date():
            raise ValidationError(_("Date of birth cannot be in the future."))
        return date_of_birth

    def save(self, commit=True):
        """Save both profile and user information"""
        profile = super().save(commit=False)
        self._update_user_fields()
        
        if commit:
            profile.user.save()
            profile.save()
            self.save_m2m()  # Important for many-to-many fields if any
            
        return profile

    def _update_user_fields(self):
        """Update the associated User model fields"""
        user = self.instance.user
        if 'first_name' in self.cleaned_data:
            user.first_name = self.cleaned_data['first_name']
        if 'last_name' in self.cleaned_data:
            user.last_name = self.cleaned_data['last_name']