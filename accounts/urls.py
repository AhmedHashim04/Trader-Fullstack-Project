from django.urls import path 
from .views import MyLoginView , RegisterView , ProfileView , UpdateProfile ,LogoutView, PasswordResetView , PasswordChangeView  
app_name = 'accounts' 

urlpatterns = [
    
    path('login/' , MyLoginView.as_view(),name='login'),
    path('logout/' , LogoutView.as_view(),name='logout'),
    path('passwordreset/' , PasswordResetView.as_view(),name='reset'),
    path('passwordchange/' ,PasswordChangeView.as_view(),name='chgpassword'),
    path('register/' ,RegisterView.as_view(),name='register'),
    path('profile/<int:pk>' ,ProfileView.as_view(),name='profile'),
    path('update_profile/<int:id>' ,UpdateProfile.as_view(),name='update_profile'),

]

