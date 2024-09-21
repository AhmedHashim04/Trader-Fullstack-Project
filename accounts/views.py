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
from .form import RegeisterForm

class MyLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'registration/login.html'



class RegisterView(CreateView):
    
    form_class = RegeisterForm
    template_name = 'registration/register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        
        return redirect ( reverse('accounts:profile',args=user.profile.PRFslug ))  # استخدم reverse_lazy مع اسم عنوان URL الصحيح

        
        




class ProfileView(DetailView):
    model = Profile
    template_name = 'account/profile.html'

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})
    
    
class UpdateProfile(UpdateView):
    model = Profile
    template_name = 'account/update_profile.html'
    context_object_name = ""
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})


class DeleteProfile(DeleteView):
    model = Profile
    

