
import pytest
from django.contrib.auth import get_user_model
from account.forms import RegisterForm, UpdateProfileForm
from account.models import Profile



"""
The tests we did
RegisterForm Validation | Make sure it accepts valid data and rejects invalid data like different passwords.
UpdateProfileForm Save | Make sure it updates the User as well, not just the Profile.
Tested missing fields | Make sure it gives an error when a field is missing.
Tested Date Input | Because we used DateInput, we need to make sure it rejects invalid dates.
Used pytest.mark.django_db | So we allow the data to go to the Database during the test.

"""


User = get_user_model()

@pytest.mark.django_db
class TestRegisterForm:

    def test_register_form_password_mismatch(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "Password$12345",
            "password2": "DifferentPassword123",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_register_form_missing_field(self):
        form_data = {
            "username": "newuser",
            # Missing email
            "password1": "Password$12345",
            "password2": "Password$12345",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

@pytest.mark.django_db
class TestUpdateProfileForm:
    def test_update_profile_form_valid_data(self):
        user = User.objects.create_user(username="testuser", password="password123")
        profile, created = Profile.objects.get_or_create(user=user)

        form_data = {
            "first_name": "Ahmed",
            "last_name": "Hashim",
            "phone_number": "0123456789",
            "address": "123 Main St",
            "city": "Cairo",
            "country": "Egypt",
            "postal_code": "12345",
            "date_of_birth": "2000-01-01",
        }
        form = UpdateProfileForm(instance=profile, data=form_data)
        assert form.is_valid()

        saved_profile = form.save()

        # Check Profile fields
        assert saved_profile.phone_number == "0123456789"
        assert saved_profile.address == "123 Main St"
        assert saved_profile.city == "Cairo"
        assert saved_profile.country == "Egypt"
        assert saved_profile.postal_code == "12345"
        
        # Check User fields updated
        user.refresh_from_db()
        assert user.first_name == "Ahmed"
        assert user.last_name == "Hashim"

    def test_update_profile_form_partial_data(self):
        user = User.objects.create_user(username="partialuser", password="password123")
        profile, created = Profile.objects.get_or_create(user=user)

        form_data = {
            # No first_name, no last_name
            "phone_number": "0987654321",
        }
        form = UpdateProfileForm(instance=profile, data=form_data)
        assert form.is_valid()

        saved_profile = form.save()

        assert saved_profile.phone_number == "0987654321"
        user.refresh_from_db()
        # First name and last name should remain unchanged (empty)
        assert user.first_name == ""
        assert user.last_name == ""

    def test_update_profile_form_invalid_date(self):
        user = User.objects.create_user(username="dateuser", password="password123")
        profile, created = Profile.objects.get_or_create(user=user)

        form_data = {
            "date_of_birth": "invalid-date",
        }
        form = UpdateProfileForm(instance=profile, data=form_data)
        assert not form.is_valid()
        assert "date_of_birth" in form.errors
