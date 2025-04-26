import pytest
from django.urls import reverse
from django.contrib.auth.models import User
import uuid

@pytest.fixture
def create_user():
    def _create_user(username='testuser', email='test@example.com', password='Password$12345', is_active=True):
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = is_active
        user.save()
        return user
    return _create_user

@pytest.mark.django_db
def test_register_view(client):
    url = reverse('account:register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'Password$12345',
        'password2': 'Password$12345'
    }

    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.count() == 1
    user = User.objects.first()
    assert not user.is_active

@pytest.mark.django_db
def test_activate_account(client, create_user):
    user = create_user(is_active=False)
    activation_key = str(uuid.uuid4())
    user.profile.activation_key = activation_key
    user.profile.save()

    url = reverse('account:activate', args=[activation_key])
    response = client.get(url)

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active
    assert user.profile.activation_key == ''

@pytest.mark.django_db
def test_profile_view(client, create_user):
    user = create_user()
    client.login(username='testuser', password='Password$12345')

    url = reverse('account:user_profile', kwargs={'id': user.profile.id})
    response = client.get(url)

    assert response.status_code == 200
    assert 'profile' in response.context
    assert response.context['profile'] == user.profile
