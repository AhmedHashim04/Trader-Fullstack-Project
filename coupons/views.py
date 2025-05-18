from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from .models import Coupon
from order.models import Order

def apply_coupon(request):
    code = request.POST.get('code')
    try:
        coupon = Coupon.objects.get(code__iexact=code , active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
        request.session['coupon_code'] = code
    except Coupon.DoesNotExist:
            messages.error(request, 'This coupon does not exist')
            return redirect('cart:cart_list')

    if not coupon.is_valid():
        messages.error('Coupon is expired or inactive')
        return redirect('cart:cart_list')

    order = Order.objects.filter(user=request.user, status='pending').first()
    if not order:
        messages.error(request, 'You have no pending orders')
        return redirect('cart:cart_list')

    if coupon.min_order_value and order.total_price < coupon.min_order_value:
        messages.error('Order value too low for this coupon')
        return redirect('cart:cart_list')

    if coupon.discount_type == 'fixed':
        discount = coupon.amount
    elif coupon.discount_type == 'percent':
        discount = order.total_price * (coupon.amount / 100)

    order.coupon = coupon
    order.discount = discount
    order.save()

    coupon.used_count += 1
    coupon.save()

    messages.success(request,'Coupon applied successfully')
    return redirect('cart:cart_list')