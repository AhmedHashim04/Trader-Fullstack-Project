from django.urls import path 
from .views import MyLoginView ,MyLogoutView, RegisterView , ProfileView , UpdateProfile , PasswordResetView , PasswordChangeView  
app_name = 'accounts' 

urlpatterns = [
    
    path('logout/' , MyLogoutView.as_view(next_page='home'),name='logout'),
    path('login/' , MyLoginView.as_view(),name='login'),
    path('passwordreset/' , PasswordResetView.as_view(),name='reset'),
    path('passwordchange/' ,PasswordChangeView.as_view(),name='chgpassword'),
    path('register/' ,RegisterView.as_view(),name='register'),
    path('profile/<slug:slug>' ,ProfileView.as_view(),name='profile'),
    path('update_profile/<slug:slug>' ,UpdateProfile.as_view(),name='update_profile'),

]

