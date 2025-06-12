from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from decimal import Decimal
from typing import Optional, Dict, Any
from django.utils import timezone
from .cart import Cart as ShoppingCart
from product.models import Product
from cart.models import Coupon
from .utils import calculate_tax, apply_discount
import logging

logger = logging.getLogger(__name__)


@require_POST
@login_required
def cart_add(request, slug):
    """
    Advanced view for adding products to cart with AJAX support and stock validation.
    """
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    referer_url = request.META.get('HTTP_REFERER', reverse('cart:cart_list'))

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity specified")
        return redirect(referer_url)

    # Stock validation
    if not product.is_available:
        messages.warning(request, f'{product.name} is currently unavailable')
        return redirect(referer_url)
    print(quantity)
    if quantity > product.stock:
        messages.warning(
            request,
            f'Only {product.stock} units available for {product.name}'
        )
        return redirect(referer_url)

    # Add to cart
    cart.add(product=product, quantity=quantity, override_quantity=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_total_items': len(cart),
            'product_total': cart.cart[str(product.slug)]['quantity']
        })

    messages.success(request, f'{product.name} added to cart successfully')
    return redirect(referer_url)


@require_POST
@login_required
def cart_remove(request, slug):
    """
    Advanced view for removing products from cart with AJAX support.
    """
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    referer_url = request.META.get('HTTP_REFERER', reverse('cart:cart_list'))

    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} removed from cart',
            'cart_total_items': len(cart)
        })

    messages.success(request, f'{product.name} removed from cart successfully')
    return redirect(referer_url)


@require_POST
@login_required
def cart_clear(request):
    """
    Clear the entire cart with confirmation and AJAX support.
    """
    cart = ShoppingCart(request)
    cart.clear()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared successfully',
            'cart_total_items': 0
        })

    messages.success(request, 'Cart cleared successfully')
    return redirect('cart:cart_list')


@method_decorator(login_required, name='dispatch')
class CartView(LoginRequiredMixin, ListView):
    """
    Advanced cart view with detailed pricing breakdown and coupon handling.
    """
    template_name = 'cart/cart.html'
    context_object_name = 'cart'
    tax_rate = Decimal('0.10')  # 10% tax

    def get_queryset(self):
        """Return the enhanced cart object with additional methods."""
        return ShoppingCart(self.request)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = context['cart']
        
        # Calculate pricing
        subtotal = cart.get_total_price()
        tax_amount = calculate_tax(subtotal, self.tax_rate)
        
        # Handle coupon
        coupon_code = self.request.session.get('coupon_code')
        coupon = self._get_valid_coupon(coupon_code) if coupon_code else None
        discount_amount = apply_discount(subtotal, coupon) if coupon else Decimal('0.00')
        
        # Final calculations
        total_after_discount = subtotal - discount_amount
        total_with_tax = total_after_discount + tax_amount

        context.update({
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'tax_rate': self.tax_rate * 100,
            'discount_amount': discount_amount,
            'total_after_discount': total_after_discount,
            'total_with_tax': total_with_tax,
            'coupon': coupon,
            'cart_summary': cart.get_cart_summary(),
        })
        return context

    def _get_valid_coupon(self, coupon_code: str) -> Optional[Coupon]:
        """
        Retrieve and validate coupon from database.
        """
        try:
            coupon = Coupon.objects.get(
                code__iexact=coupon_code,
                active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            if not coupon.is_valid_for_user(self.request.user):
                messages.warning(self.request, "This coupon is not valid for your account")
                del self.request.session['coupon_code']
                return None
            return coupon
        except Coupon.DoesNotExist:
            logger.warning(f"Invalid coupon attempt: {coupon_code}")
            messages.warning(self.request, "Invalid or expired coupon code")
            del self.request.session['coupon_code']
            return None

@require_POST
@login_required
def apply_coupon(request):
    """
    Dedicated view for applying coupons to the cart.
    """
    coupon_code = request.POST.get('coupon_code', '').strip()
    if not coupon_code:
        messages.error(request, "Please enter a coupon code")
        return redirect('cart:cart_list')

    cart = ShoppingCart(request)
    try:
        coupon = Coupon.objects.get(
            code__iexact=coupon_code,
            active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        
        if not coupon.is_valid_for_user(request.user):
            messages.warning(request, "This coupon is not valid for your account")
            return redirect('cart:cart_list')

        request.session['coupon_code'] = coupon.code
        messages.success(request, f"Coupon '{coupon.code}' applied successfully")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'discount_amount': apply_discount(cart.get_total_price(), coupon),
                'coupon_code': coupon.code
            })
            
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid or expired coupon code")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': "Invalid coupon code"})

    return redirect('cart:cart_list')


# from django.shortcuts import redirect
# from django.utils import timezone
# from django.contrib import messages
# from ..cart.models import Coupon
# from order.models import Order

# def apply_coupon(request):
#     code = request.POST.get('code')
#     try:
#         coupon = Coupon.objects.get(code__iexact=code , active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
#         request.session['coupon_code'] = code
#     except Coupon.DoesNotExist:
#             messages.error(request, 'This coupon does not exist')
#             return redirect('cart:cart_list')

#     if not coupon.is_valid():
#         messages.error('Coupon is expired or inactive')
#         return redirect('cart:cart_list')

#     order = Order.objects.filter(user=request.user, status='pending').first()
#     if not order:
#         messages.error(request, 'You have no pending orders')
#         return redirect('cart:cart_list')

#     if coupon.min_order_value and order.total_price < coupon.min_order_value:
#         messages.error('Order value too low for this coupon')
#         return redirect('cart:cart_list')



#     if coupon.discount_type == 'fixed':
#         discount = coupon.amount
#     elif coupon.discount_type == 'percent':
#         discount = order.total_price * (coupon.amount / 100)

#     order.coupon = coupon
#     order.discount = discount
#     order.save()

#     coupon.used_count += 1
#     coupon.save()

#     messages.success(request,'Coupon applied successfully')
#     return redirect('cart:cart_list')
