from django.urls import path
from .views import pay_by_vodafone , PaymentSuccessView
app_name = 'payment'

urlpatterns = [
    path('', pay_by_vodafone, name='payment'),
    path('success/', PaymentSuccessView.as_view(), name='success'),
]
 