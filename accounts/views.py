from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import  DetailView , FormView , UpdateView , DeleteView ,CreateView
from django.contrib.auth import login 
from django.contrib.auth.views import LoginView , LogoutView , PasswordResetView , PasswordChangeView 
from django.urls import reverse  , reverse_lazy
from .models import Profile
from .form import RegeisterForm , UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin 
import uuid
from django.core.mail import send_mail


class MyLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'registration/login.html'
    
class MyLogoutView(LogoutView):
    redirect_authenticated_user = True
    template_name = 'registration/logout.html'
    next_page = 'home'



class LogoutRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home') 
        return super().dispatch(request, *args, **kwargs)


class ActivateAccountView(View):
    def get(self, request, activation_key):
        user = get_object_or_404(User, activation_key=activation_key)
        user.is_active = True
        user.activation_key = ''  
        user.save()
        messages.success(request, 'Account Had Activated Successfuly !')
        
        return redirect('accounts:login')

class RegisterView(LogoutRequiredMixin,CreateView):
    form_class    = RegeisterForm
    template_name = 'registration/register.html'
    success_url   = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.activation_key = str(uuid.uuid4())  # إنشاء مفتاح تفعيل

        # إرسال البريد الإلكتروني
        activation_link = f"http://127.0.0.1:8000/accounts/activate/{user.activation_key}/"
        send_mail(
            'Activate your account',
            f'Click the link to activate your account: {activation_link}',
            'ahmedha4im7@gmail.com',
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Account Registerd Successfuly !')
        messages.success(self.request, 'Please Active your account we had sent email  !')
        user = form.save()
        
        login(self.request,user)

        return super().form_valid(form)



class ProfileView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'account/profile.html'
    slug_field = "PRFslug"
    slug_url_kwarg = "slug"
    context_object_name = "profile"

    def get_absolute_url(self):
        obj = self.get_object() 
        return reverse('accounts:profile', kwargs={self.slug_url_kwarg: getattr(obj, self.slug_field)})


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'account/update_profile.html'
    form_class = UpdateProfileForm
    slug_field = "PRFslug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your Profile had updated successfuly  !')
        return super().form_valid(form)  # استدعاء الدالة الأساسية

    def get_success_url(self):
        obj = self.get_object()  # جلب الكائن الحالي
        return reverse('accounts:profile', kwargs={self.slug_url_kwarg: obj.PRFslug})