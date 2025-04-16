from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import redirect , get_object_or_404
from django.views.generic import  DetailView  , UpdateView ,CreateView
from django.contrib.auth.views import LoginView , LogoutView 
from django.urls import reverse  , reverse_lazy
from .models import Profile
from django.contrib.auth.models import User
from .form import RegisterForm , UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.core.mail import send_mail
from django.conf import settings


class MyLoginView(LoginView):
    redirect_authenticated_user = True

class MyLogoutView(LogoutView):
    next_page = 'home'



class ActivateAccountView(View):
    def get(self, request, activation_key):

        user = get_object_or_404(User, activation_key=activation_key)
        if user:
            user.is_active = True
            user.activation_key = ''
            user.save()
            messages.success(request, 'Account Had Activated Successfuly !')
        else:
            messages.error(request, 'Activation Failed , Invalid key !')
        return redirect('account:login')




class RegisterView(CreateView):
    form_class    = RegisterForm
    template_name = 'registration/register.html'
    success_url   = reverse_lazy('account:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        self.send_activation_email(user)
        messages.success(self.request, 'Account created successfully! Please check your email to activate your account.')
        return response

    def send_activation_email(self, user):
        activation_key = user.activation_key  # Assuming activation_key is generated and saved with the user model
        activation_url = self.request.build_absolute_uri(reverse('account:auth-activate', args=[activation_key]))
        subject = 'Activate Your Account'
        message = f'Please click the link to activate your account: {activation_url}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        print(subject, message, settings.EMAIL_HOST_USER, [user.email])

class ProfileView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'account/profile.html'
    context_object_name = "profile"
    slug_field = "id"
    slug_url_kwarg = "id"

    def get_absolute_url(self):
        obj = self.get_object() 
        return reverse('account:profile', kwargs={self.slug_url_kwarg: getattr(obj, self.slug_field)})


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'account/update_profile.html'
    form_class = UpdateProfileForm
    slug_field = "id"
    slug_url_kwarg = "id"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your Profile had updated successfuly  !')
        return super().form_valid(form)  
    def get_success_url(self):
        obj = self.get_object()  
        return reverse('account:profile', kwargs={self.slug_url_kwarg: obj.slug_field})