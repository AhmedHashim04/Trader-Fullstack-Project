from django.contrib.auth import login
from cart.cart import Cart
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
from django.http import Http404
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)
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

        logger.info(f"New user registered: {user.email}")
        from django.template.loader import render_to_string

        
        self.send_activation_email(user)
        messages.success(self.request, 'Account created successfully! Please check your email to activate your account.')
        return super().form_valid(form)

    def send_activation_email(self, user):
        activation_key = str(uuid.uuid4())
        user.profile.activation_key = activation_key
        user.profile.save()
        activation_url = self.request.build_absolute_uri(reverse('account:activate', args=[activation_key]))

        subject = 'Activate Your Account'
        # expiry_date = timezone.now() + timezone.timedelta(hours=24)  # صلاحية الرابط لمدة 24 ساعة
        # user.profile.activation_key_expires = expiry_date  # إضافة تاريخ انتهاء الصلاحية

        # from django.template.loader import render_to_string
        # subject = 'Activate Your Account'
        # message = render_to_string('account/activation_email.html', {
        #     'user': user,
        #     'activation_url': activation_url,
        # })
        # from django.core.mail import send_mail
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        message = f'Please click the link to activate your account: {activation_url}'
        print(subject, message, settings.EMAIL_HOST_USER, [user.email])


class WaitingActivation(TemplateView):
    template_name = "account/waiting_activation.html"
    
class ActivateAccountView(View):
    def get(self, request, activation_key):
        try:
            user = User.objects.select_related('profile').get(profile__activation_key=activation_key)
        except User.DoesNotExist:
            messages.error(request, 'Invalid or expired activation link.')
            raise Http404("User not found")
        # try:
        #     user = User.objects.select_related('profile').get(profile__activation_key=activation_key,profile__activation_key_expires__gt=timezone.now(),is_active=False)
        # except User.DoesNotExist:
        #     messages.error(request, 'Invalid or expired activation link.')
        #     return redirect('account:register')
        # user = get_object_or_404(User, profile__activation_key=activation_key,profile__activation_key_expires__gt=timezone.now(),is_active=False)
        if user.is_active:
            messages.info(request, 'Your account is already activated.')
            return redirect('home:home')

        user.is_active = True
        user.profile.activation_key = ''
        # user.profile.activation_key_expires = None
        login(request, user)
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return render(request, 'account/account_activation_complete.html')


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'account/profile.html'
    context_object_name = "profile"
    pk_url_kwarg = "id"

    def get_queryset(self):
        return super().get_queryset().select_related('user')

class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'account/update_profile.html'
    form_class = UpdateProfileForm
    context_object_name = "profile"
    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        # Prevent access if not the profile owner
        profile = self.get_object()
        if profile.user != request.user:
            raise Http404("You cannot edit this profile.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully!')
        return response

    def get_success_url(self):
        if self.request.user.profile.id != self.object.id:
            raise Http404("You cannot update this profile.")
        return reverse('account:user_profile', kwargs={'id': self.object.id})

from django.contrib import messages

class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        old_session_key = self.request.session.session_key
        response = super().form_valid(form)
        added_items_count = Cart.merge_on_login(self.request.user, old_session_key)
        if added_items_count > 0:
            messages.info(
                self.request, 
                f"{added_items_count} item(s) from your previous cart have been merged into your current cart."
            )

        return response

class MyLogoutView(LogoutView):
    next_page = 'home:home'
    http_method_names = ["post", "options"]

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} logged out")
        return super().dispatch(request, *args, **kwargs)


class MyPasswordResetPassword(PasswordResetView):
    success_url = reverse_lazy("account:password_reset_done")

