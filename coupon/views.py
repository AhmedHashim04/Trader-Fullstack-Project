from django.shortcuts import render, redirect, get_object_or_404
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
                CouponUsage.objects.create(coupon=coupon, user=request.user, discount_amount=coupon.amount)
                coupon.used_count += 1
                coupon.save()
                cart = ShoppingCart(request)
                cart_total = cart.get_total_price_after_discount()
                if coupon.is_valid(user=request.user, cart_total=cart_total):
                    # Apply coupon to session
                    request.session['coupon_id'] = coupon.id
                    request.session['coupon_code'] = coupon.code
                    request.session['coupon_discount'] = str(coupon.apply_discount(cart_total))
                    request.session['cart_total'] =  str(cart_total - coupon.apply_discount(cart_total))

                    messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
                else:
                    messages.error(request, 'This coupon is not valid or has expired.')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')
        else:
            messages.error(request, 'Invalid coupon code format.')
    
    return redirect('cart:cart_list')  # Redirect to cart page or wherever you want

@login_required
def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['coupon_code']
        del request.session['coupon_discount']
        messages.success(request, 'Coupon removed successfully.')
    return redirect('cart:cart_list')

@login_required
def my_coupons(request):
    # Get coupons used by the current user
    used_coupons = CouponUsage.objects.filter(user=request.user).select_related('coupon')
    
    context = {
        'used_coupons': used_coupons,
        'title': 'My Coupons'
    }
    return render(request, 'coupon/my_coupons.html', context)