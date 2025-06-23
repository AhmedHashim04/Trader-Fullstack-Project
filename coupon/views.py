from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coupon, CouponUsage
from .forms import CouponApplyForm
from cart.cart import Cart as ShoppingCart


def store_coupon_in_session(request, coupon, discount_amount):
    request.session['coupon'] = {
        "id": coupon.id,
        "code": coupon.code,
        "amount": str(coupon.amount),
        "discount": str(discount_amount),
        "type": coupon.discount_type,
    }

def remove_coupon_from_session(request):
    request.session.pop('coupon', None)

def get_coupon_from_session(request):
    return request.session.get('coupon')


def coupon_list(request):
    coupons = Coupon.objects.filter(active=True)
    context = {
        'coupons': coupons,
        'title': 'Available Coupons'
    }
    return render(request, 'coupon/coupon_list.html', context)

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code=code)
                cart = ShoppingCart(request)
                cart_total = cart.get_total_price_after_discount_and_tax()
                
                if coupon.is_valid(user=request.user, cart_total=cart_total):
                    discount_amount = coupon.apply_discount(cart_total)
                    
                    CouponUsage.objects.create(
                        coupon=coupon, 
                        user=request.user, 
                        discount_amount=discount_amount
                    )
                    coupon.used_count += 1
                    coupon.save()
                    store_coupon_in_session(request, coupon, discount_amount)
                    
                    messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
                else:
                    messages.error(request, 'This coupon is not valid or has expired.')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')
        else:
            messages.error(request, 'Invalid coupon code format.')
    
    return redirect('cart:cart_list')

@login_required
def remove_coupon(request):
    if 'coupon' in request.session:
        remove_coupon_from_session(request)
        messages.success(request, 'Coupon removed successfully.')
    return redirect('cart:cart_list')

@login_required
def my_coupons(request):

    used_coupons = CouponUsage.objects.filter(user=request.user).select_related('coupon')
    
    context = {
        'used_coupons': used_coupons,
        'title': 'My Coupons'
    }
    return render(request, 'coupon/my_coupons.html', context)
