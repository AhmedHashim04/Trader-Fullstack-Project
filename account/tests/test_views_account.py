
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core import mail
from django.contrib.messages import get_messages
from account.models import Profile
from django.test import Client
from django.core.exceptions import ValidationError

User = get_user_model()
pytestmark = pytest.mark.django_db

client = Client()

def test_register_view_creates_inactive_user():
    response = client.post(reverse("account:register"), {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": "StrongPass123",
        "password2": "StrongPass123",
    }, follow=True)

    user = User.objects.get(username="newuser")
    assert user.is_active is False
    assert user.profile.activation_key != ""
    messages = list(get_messages(response.wsgi_request))
    assert any("Account created successfully" in str(m) for m in messages)
    assert response.status_code == 200

def test_register_redirects_authenticated_user(client, django_user_model):
    user = django_user_model.objects.create_user(username="authuser", password="pass")
    client.login(username="authuser", password="pass")
    response = client.get(reverse("account:register"))
    assert response.status_code == 302
    assert response.url == reverse("home:home")

def test_activate_account_success():
    user = User.objects.create_user(username="toactivate", email="user@example.com", password="123")
    user.is_active = False
    user.save()
    user.profile.activation_key = "activate123"
    user.profile.save()

    url = reverse("account:activate", args=["activate123"])
    response = client.get(url, follow=True)
    user.refresh_from_db()

    assert user.is_active is True
    assert user.profile.activation_key == ""
    assert response.status_code == 200
    assert b"Your account has been activated successfully" in response.content

def test_activate_account_already_active():
    user = User.objects.create_user(username="alreadyactive", email="already@example.com", password="123", is_active=True)
    user.profile.activation_key = "somekey"
    user.profile.save()
    response = client.get(reverse("account:activate", args=["somekey"]))
    assert response.status_code == 302
    assert response.url == reverse("home:home")

def test_activate_account_invalid_key():
    response = client.get(reverse("account:activate", args=["wrongkey"]), follow=True)
    assert response.status_code == 404

def test_profile_view_authenticated(client, django_user_model):
    user = django_user_model.objects.create_user(username="prof", password="pass")
    client.login(username="prof", password="pass")
    url = reverse("account:user_profile", kwargs={"id": user.profile.id})
    response = client.get(url)
    assert response.status_code == 200

def test_update_profile_only_by_owner(client, django_user_model):
    user = django_user_model.objects.create_user(username="owner", password="pass")
    other = django_user_model.objects.create_user(username="other", password="pass")
    client.login(username="owner", password="pass")
    url = reverse("account:user_profile_edit", kwargs={"id": other.profile.id})
    response = client.get(url)
    assert response.status_code == 404

# def test_update_profile_success(client, django_user_model):
#     user = django_user_model.objects.create_user(username="editme", password="pass")
#     client.login(username="editme", password="pass")
#     url = reverse("account:user_profile_edit", kwargs={"id": user.profile.id})
#     response = client.post(url, {"email": "edit@me.com"}, follow=True)
#     user.profile.refresh_from_db()
#     assert response.status_code == 200
#     assert user.profile.email == "edit@me.com"

def test_login_updates_last_login(client, django_user_model):
    user = django_user_model.objects.create_user(username="loginuser", password="pass")
    url = reverse("account:login")
    response = client.post(url, {"username": "loginuser", "password": "pass"})
    user.refresh_from_db()
    assert user.last_login is not None

def test_logout_logs_user(client, django_user_model):
    user = django_user_model.objects.create_user(username="logoutuser", password="pass")
    client.login(username="logoutuser", password="pass")
    response = client.post(reverse("account:logout"))
    assert response.status_code == 302
    assert response.url == reverse("home:home")

def test_invalid_phone_number_raises_error():
    user = User.objects.create_user(username="invalid_phone")
    profile = user.profile
    profile.phone_number = "12345"  # رقم خاطئ
    with pytest.raises(ValidationError):
        profile.full_clean()

def test_invalid_postal_code_raises_error():
    user = User.objects.create_user(username="invalid_postal")
    profile = user.profile
    profile.postal_code = "000"  # كود بريدي خاطئ
    with pytest.raises(ValidationError):
        profile.full_clean()

def test_invalid_address_raises_error():
    user = User.objects.create_user(username="invalid_address")
    profile = user.profile
    profile.address = "123 Main St"  # مش بالعربي
    with pytest.raises(ValidationError):
        profile.full_clean()
