from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import DetailView, UpdateView, CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import reverse, reverse_lazy
from .models import Profile
from django.contrib.auth.models import User
from .forms import RegisterForm, UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.mail import send_mail
from django.conf import settings
import uuid


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('account:waiting_activation')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        self.send_activation_email(user)
        messages.success(self.request, 'Account created successfully! Please check your email to activate your account.')
        return super().form_valid(form)

    def send_activation_email(self, user):
        activation_key = str(uuid.uuid4())
        user.profile.activation_key = activation_key
        user.profile.save()
        activation_url = self.request.build_absolute_uri(reverse('account:activate', args=[activation_key]))
        subject = 'Activate Your Account'
        message = f'Please click the link to activate your account: {activation_url}'
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        print(subject, message, settings.EMAIL_HOST_USER, [user.email])


class WaitingActivation(TemplateView):
    template_name = "account/waiting_activation.html"
    
class ActivateAccountView(View):
    def get(self, request, activation_key):
        user = get_object_or_404(User, profile__activation_key=activation_key)
        if user.is_active:
            messages.info(request, 'Your account is already activated.')
            return redirect('home:home')

        user.is_active = True
        user.profile.activation_key = ''
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return render(request, 'account/account_activation_complete.html')


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'account/profile.html'
    context_object_name = "profile"
    pk_url_kwarg = "id"


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'account/update_profile.html'
    form_class = UpdateProfileForm
    context_object_name = "profile"
    pk_url_kwarg = "id"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account:user_profile', kwargs={'id': self.object.id})


class MyLoginView(LoginView):
    redirect_authenticated_user = True


class MyLogoutView(LogoutView):
    next_page = 'home:home'
    http_method_names = ["get", "options"]

    def get(self, request, *args, **kwargs):
        """Logout may be done via GET."""
        logout(request)
        redirect_to = self.get_success_url()
        if redirect_to != request.get_full_path():
            # Redirect to target page once the session has been cleared.
            return HttpResponseRedirect(redirect_to)
        return super().get(request, *args, **kwargs)


class MyPasswordResetPassword(PasswordResetView):
    success_url = reverse_lazy("account:password_reset_done")

