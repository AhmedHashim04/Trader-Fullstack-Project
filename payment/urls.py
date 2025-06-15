from django.urls import path
from .views import payment_callback
app_name = 'payment'

urlpatterns = [

    path("payment/callback/", payment_callback, name="payment_callback")


]
 