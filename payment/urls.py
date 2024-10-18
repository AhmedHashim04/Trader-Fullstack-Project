from django.urls import path
from .views import PaymentView, PaymentSuccessView

app_name = 'payment'

urlpatterns = [
    path('', PaymentView.as_view(), name='payment'),
    path('success/', PaymentSuccessView.as_view(), name='success'),
]
 