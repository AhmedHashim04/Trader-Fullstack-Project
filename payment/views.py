
from django.shortcuts import redirect

from cart.cart import Cart as ShoppingCart
from django.shortcuts import redirect
from .utils.paymob import get_auth_token, create_paymob_order, generate_payment_key
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import hmac
import hashlib

def pay_with_paymob(request):
    cart = ShoppingCart(request)
    amount_cents = int(cart.get_total_price_after_discount_and_tax() * 100)

    token = get_auth_token()

    order_id = create_paymob_order(token, amount_cents)

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

    payment_token = generate_payment_key(token, order_id, amount_cents, billing_data)

    redirect_url = f"https://accept.paymobsolutions.com/api/acceptance/iframes/your_iframe_id?payment_token={payment_token}"
    return redirect(redirect_url)

@csrf_exempt
def payment_callback(request):
    data = request.POST.dict()
    
    # Verify HMAC signature (مهم للأمان)
    hmac_secret = b'your_hmac_secret'
    sent_hmac = data.get("hmac")
    computed_hmac = hmac.new(hmac_secret, msg=request.body, digestmod=hashlib.sha512).hexdigest()

    if hmac.compare_digest(sent_hmac, computed_hmac):
        if data.get("success") == "true":
            order_id = data.get("order")
            # حدّث الطلب في DB: order.status = 'paid'
            return HttpResponse("OK")
    
    return HttpResponse("FAILED", status=400)