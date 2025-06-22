
from .utils.paymob import get_auth_token, create_paymob_order, generate_payment_key
from django.shortcuts import redirect, get_object_or_404
from order.models import Order
from .forms import PaymentProofForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from .models import VodafoneCashPayment

def pay_with_paymob(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    amount_cents = int(order.total_price * 100)

    token = get_auth_token()

    # هنا خلطت بين ID تبع Django و Paymob - لازم اسم مختلف
    paymob_order_id = create_paymob_order(token, amount_cents)

    billing_data = {
        "first_name": request.user.first_name or "Ahmed",
        "last_name": request.user.last_name or "Hashim",
        "email": request.user.email or "ahmed@example.com",
        "phone_number": "01000000000",
        "city": "Cairo",
        "country": "EG",
        "street": "Street 123",
        "building": "1",
        "floor": "2",
        "apartment": "3",
    }

    payment_token = generate_payment_key(token, paymob_order_id, amount_cents, billing_data)

    iframe_id = "PUT_YOUR_IFRAME_ID_HERE"
    redirect_url = f"https://accept.paymobsolutions.com/api/acceptance/iframes/{iframe_id}?payment_token={payment_token}"
    return redirect(redirect_url)

import hashlib
import hmac
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from order.models import Order


@csrf_exempt
def payment_callback(request):
    data = request.POST.dict()

    # ترتيب الحقول حسب توثيق Paymob
    keys_to_hash = [
        'amount_cents',
        'created_at',
        'currency',
        'error_occured',
        'has_parent_transaction',
        'id',
        'integration_id',
        'is_3d_secure',
        'is_auth',
        'is_capture',
        'is_refunded',
        'is_standalone_payment',
        'is_voided',
        'order',
        'owner',
        'pending',
        'source_data_pan',
        'source_data_sub_type',
        'source_data_type',
        'success',
    ]

    hmac_secret = b"PUT_YOUR_HMAC_SECRET_HERE"
    message = ''

    for key in keys_to_hash:
        message += data.get(key, '')

    computed_hmac = hmac.new(hmac_secret, message.encode('utf-8'), hashlib.sha512).hexdigest()
    sent_hmac = data.get("hmac")

    if hmac.compare_digest(computed_hmac, sent_hmac):
        if data.get("success") == "true":
            paymob_order_id = data.get("order")
            try:
                # اربط الطلب ب Paymob ID مثلاً
                order = Order.objects.get(paymob_order_id=paymob_order_id)
                order.status = "paid"
                order.save()
                return HttpResponse("OK")
            except Order.DoesNotExist:
                return HttpResponse("Order not found", status=404)

    return HttpResponse("FAILED", status=400)




@login_required
def resend_payment_proof(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = VodafoneCashPayment.objects.filter(order=order).first()
    if payment:
        print(payment)
        payment.delete()
        order.status = "pending"
        order.save()

    return redirect(reverse("order:order_detail", kwargs={"pk": order_id}))
