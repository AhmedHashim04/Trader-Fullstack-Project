from django.urls import path 
from .views import MyLoginView ,MyLogoutView, RegisterView , ProfileView , UpdateProfile , ActivateAccountView ,WaitingActivation, MyPasswordResetPassword
from django.contrib.auth import views as auth_views
app_name = 'account' 

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('login/', MyLoginView.as_view(), name='login'),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),

    path('password_reset/', MyPasswordResetPassword.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('active/',WaitingActivation.as_view(),name='waiting_activation'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('activate/<str:activation_key>/', ActivateAccountView.as_view(), name='activate'),
    
    path('profile/<str:id>/', ProfileView.as_view(), name='user_profile'),
    path('profile/<str:id>/edit/', UpdateProfile.as_view(), name='user_profile_edit'),
]

