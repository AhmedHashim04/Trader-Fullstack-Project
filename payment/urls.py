from django.urls import path
from .views import payment_callback, pay_with_paymob ,resend_payment_proof
app_name = 'payment'

urlpatterns = [

    path("paymob/", pay_with_paymob, name="pay_with_paymob"),
    path("callback/", payment_callback, name="payment_callback"),
    path("resend-proof/<uuid:order_id>/", resend_payment_proof, name="resend_payment_proof"),

]
