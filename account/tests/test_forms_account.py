import pytest
from django.utils import timezone
from account.forms import RegisterForm, UpdateProfileForm
from django.contrib.auth import get_user_model
from account.models import Profile

User = get_user_model()
pytestmark = pytest.mark.django_db

def test_register_form_valid():
    form = RegisterForm(data={
        "username": "ahmed",
        "email": "ahmed@example.com",
        "password1": "StrongPass123",
        "password2": "StrongPass123"
    })
    assert form.is_valid()

def test_register_form_invalid_password_mismatch():
    form = RegisterForm(data={
        "username": "ahmed",
        "email": "ahmed@example.com",
        "password1": "pass1",
        "password2": "pass2"
    })
    assert not form.is_valid()
    assert "password2" in form.errors

def test_register_form_duplicate_email():
    User.objects.create_user(username="existing", email="ahmed@example.com", password="123")
    form = RegisterForm(data={
        "username": "newuser",
        "email": "ahmed@example.com",
        "password1": "StrongPass123",
        "password2": "StrongPass123"
    })
    assert not form.is_valid()
    assert "email" in form.errors

def test_register_form_invalid_username():
    form = RegisterForm(data={
        "username": "###",
        "email": "user@example.com",
        "password1": "StrongPass123",
        "password2": "StrongPass123"
    })
    assert not form.is_valid()
    assert "username" in form.errors

def test_update_profile_form_valid(django_user_model):
    user = django_user_model.objects.create_user(username="ahmed", password="123")
    profile = user.profile
    form = UpdateProfileForm(data={
        "first_name": "Ahmed",
        "last_name": "Hashim",
        "phone_number": "01012345678",
        "address": "شارع النيل",
        "city": "الجيزة",
        "country": "مصر",
        "postal_code": "12345",
        "date_of_birth": "2000-01-01",
    }, instance=profile)
    assert form.is_valid()
    updated_profile = form.save()
    assert updated_profile.phone_number == "01012345678"

def test_update_profile_invalid_phone():
    form = UpdateProfileForm(data={
        "phone_number": "ABC1234567"
    })
    assert not form.is_valid()
    assert "phone_number" in form.errors

def test_update_profile_future_dob(django_user_model):
    user = django_user_model.objects.create_user(username="ahmed", password="123")
    profile = user.profile
    future_date = timezone.now().date().replace(year=timezone.now().year + 1)
    form = UpdateProfileForm(data={
        "date_of_birth": future_date
    }, instance=profile)
    assert not form.is_valid()
    assert "date_of_birth" in form.errors
