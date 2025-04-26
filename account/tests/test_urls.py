import pytest
from django.urls import reverse, resolve
from account.views import MyLoginView, MyLogoutView, RegisterView, ProfileView, UpdateProfile, ActivateAccountView, WaitingActivation, MyPasswordResetPassword
from django.contrib.auth import views as auth_views

@pytest.mark.parametrize("url_name, view_class, url_kwargs", [
    ('account:register', RegisterView, {}),
    ('account:logout', MyLogoutView, {}),
    ('account:login', MyLoginView, {}),
    ('account:password_change', auth_views.PasswordChangeView, {}),
    ('account:password_reset', MyPasswordResetPassword, {}),
    ('account:password_reset_done', auth_views.PasswordResetDoneView, {}),
    ('account:waiting_activation', WaitingActivation, {}),
    ('account:password_reset_confirm', auth_views.PasswordResetConfirmView, {'uidb64': 'uid', 'token': 'token'}),
    ('account:password_reset_complete', auth_views.PasswordResetCompleteView, {}),
    ('account:activate', ActivateAccountView, {'activation_key': 'key'}),
    ('account:user_profile', ProfileView, {'id': '1'}),
    ('account:user_profile_edit', UpdateProfile, {'id': '1'}),
])
def test_url_resolves_to_correct_view(url_name, view_class, url_kwargs):
    url = reverse(url_name, kwargs=url_kwargs)
    assert resolve(url).func.view_class == view_class

