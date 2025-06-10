from django.urls import path
from .views import PaymentSuccessView,confirm_vodafone_payment#  pay_by_vodafone , 
app_name = 'payment'

urlpatterns = [
    # path('', pay_by_vodafone, name='payment'),
    path('', confirm_vodafone_payment, name='payment'),
    path('success/', PaymentSuccessView.as_view(), name='success'),
]
 