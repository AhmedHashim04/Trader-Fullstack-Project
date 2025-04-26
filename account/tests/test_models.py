import pytest

from django.contrib.auth.models import User
from account.models import Profile
from product.models import Product

"""
Create a valid Profile with basic data.

The relationship with User works (OneToOneField).

Wishlist works and products can be added.

Wishlist Count Property returns the correct number.

String Representation (__str__) returns the correct text.

Signal automatically creates a Profile when a User registers.

"""


@pytest.mark.django_db
class TestProfileModel:

    def test_profile_creation(self):
        user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        profile = Profile.objects.get(user=user)
        print(profile)
        assert profile.email == ""
        assert profile.user.username == "testuser"

    def test_string_representation(self):
        user = User.objects.create_user(username="testuser", first_name="Test", last_name="User", email="test@example.com", password="password123")
        profile = Profile.objects.get(user=user)

        assert str(profile) == "Test User's Profile"

    def test_wishlist_functionality(self):
        user = User.objects.create_user(username="wishlistuser", email="wishlist@example.com", password="password123")
        profile = Profile.objects.get(user=user)
        product1 = Product.objects.create(name="Product 1", price=10,cost=5)
        product2 = Product.objects.create(name="Product 2", price=20)

        profile.wishlist.add(product1, product2)

        assert profile.wishlist.count() == 2
        assert profile.wishlist_count == 2

    def test_profile_auto_created_on_user_creation(self):
        user = User.objects.create_user(username="autosignal", email="signal@example.com", password="password123")
        assert Profile.objects.filter(user=user).exists()
