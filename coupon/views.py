from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coupon, CouponUsage
from .forms import CouponApplyForm
from cart.cart import Cart as ShoppingCart

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
                    
                    # Record usage AFTER validation
                    CouponUsage.objects.create(
                        coupon=coupon, 
                        user=request.user, 
                        discount_amount=discount_amount
                    )
                    coupon.used_count += 1
                    coupon.save()
                    
                    request.session['coupon_id'] = coupon.id
                    request.session['coupon_code'] = coupon.code
                    request.session['coupon_amount'] = str(coupon.amount)
                    request.session['coupon_discount'] = str(discount_amount)
                    request.session['discount_type'] = str(coupon.discount_type)
                    
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
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['coupon_code']
        del request.session['coupon_amount']
        del request.session['coupon_discount']
        del request.session['discount_type']

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
