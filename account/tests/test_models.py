
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from account.models import Profile
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from product.models import Product

User = get_user_model()

pytestmark = pytest.mark.django_db

def test_profile_created_with_user():
    user = User.objects.create_user(username="testuser", password="pass")
    assert hasattr(user, 'profile')
    assert isinstance(user.profile, Profile)

def test_email_auto_copied_from_user():
    user = User.objects.create_user(username="test2", email="user@example.com", password="pass")
    profile = user.profile
    assert profile.email == "user@example.com"

def test_age_property():
    user = User.objects.create_user(username="test3")
    profile = user.profile
    profile.date_of_birth = date(2000, 1, 1)
    profile.save()
    today = timezone.now().date()
    expected_age = today.year - 2000 - ((today.month, today.day) < (1, 1))

    assert profile.age == expected_age

def test_age_none_if_no_dob():
    user = User.objects.create_user(username="test4")
    profile = user.profile
    assert profile.age is None

def test_activation_key_expired_true():
    user = User.objects.create_user(username="test5")
    profile = user.profile
    profile.activation_key_expires = timezone.now() - timedelta(days=1)
    assert profile.is_activation_key_expired() is True

def test_activation_key_expired_false():
    user = User.objects.create_user(username="test6")
    profile = user.profile
    profile.activation_key_expires = timezone.now() + timedelta(days=1)
    assert profile.is_activation_key_expired() is False

# def test_get_city_display_ar():
#     user = User.objects.create_user(username="test7")
#     profile = user.profile
#     profile.city = Profile.Cities.CAIRO
#     assert profile.get_city_display_ar() == "القاهرة"

def test_wishlist_count():
    user = User.objects.create_user(username="test8")
    product = Product.objects.create(name="Test", price=100)
    profile = user.profile
    profile.wishlist.add(product)
    assert profile.wishlist_count == 1
