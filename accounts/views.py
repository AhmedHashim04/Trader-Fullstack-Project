from django.contrib.auth.forms import AuthenticationForm
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.views.generic import ListView , TemplateView , DetailView , FormView , UpdateView , DeleteView ,CreateView
from django.contrib.auth import login , logout 
from django.contrib.auth.views import LoginView , LogoutView , PasswordResetView , PasswordChangeView 
from django.urls import reverse  , reverse_lazy
from .models import Profile
from .form import RegeisterForm , UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin 

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

class RegisterView(LogoutRequiredMixin,CreateView):
    
    form_class = RegeisterForm
    template_name = 'registration/register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        
        return redirect ( reverse('accounts:profile',args=user.profile.PRFslug ))  # استخدم reverse_lazy مع اسم عنوان URL الصحيح

        
        




class ProfileView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'account/profile.html'
    slug_field = "PRFslug"
    slug_url_kwarg = "slug"
    context_object_name = "profile"

    def get_absolute_url(self):
        obj = self.get_object()  # جلب الكائن الحالي
        return reverse('accounts:profile', kwargs={self.slug_url_kwarg: getattr(obj, self.slug_field)})


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'account/update_profile.html'
    form_class = UpdateProfileForm
    slug_field = "PRFslug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        form.save()
        obj = self.get_object()  # جلب الكائن الحالي
        return super().form_valid(form)  # استدعاء الدالة الأساسية

    def get_success_url(self):
        obj = self.get_object()  # جلب الكائن الحالي
        return reverse('accounts:profile', kwargs={self.slug_url_kwarg: obj.PRFslug})