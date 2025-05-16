from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from .cart import Cart as cart_branch
from product.models import Product
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from coupons.models import Coupon  # تأكد إن ده هو المسار الصح للموديل بتاع الكوبون

@login_required
def cart_add(request, slug):
    """Add a product to the cart."""
    cart = cart_branch(request)
    product = get_object_or_404(Product, slug=slug)

    if product.stock < 1:
        messages.warning(request, f'{product.name} is out of stock. Available stock: {product.stock}')
        return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))

    quantity = int(request.POST.get('quantity', 1))
    if quantity > product.stock:
        messages.warning(request, f'Cannot add {quantity} units of {product.name}. Only {product.stock} available.')
        return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))

    cart.add(product=product, quantity=quantity, override_quantity=True)
    messages.success(request, f'{product.name} added to cart successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))


@login_required
def cart_remove(request, slug):
    """Remove a product from the cart."""
    cart = cart_branch(request)
    product = get_object_or_404(Product, slug=slug)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))


@login_required
def cart_clear(request):
    """Clear the cart."""
    cart = cart_branch(request)
    cart.clear()
    messages.success(request, 'Cart cleared successfully.')
    return redirect('cart:cart_list')

class CartView(LoginRequiredMixin, ListView):
    """Display the cart."""
    template_name = 'cart/cart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        """Return the items in the cart."""
        cart = cart_branch(self.request)
        return cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = context['cart']

        subtotal = cart.get_total_price()
        tax = 10
        discount_amount = 0
        coupon_obj = None
        discount_type = None

        coupon_code = self.request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code__iexact=coupon_code)
                if coupon_obj.is_valid():
                    discount_type = coupon_obj.discount_type
                    if discount_type == 'percent':
                        discount_amount = subtotal * (coupon_obj.amount / 100)
                    elif discount_type == 'fixed':
                        discount_amount = coupon_obj.amount
            except Coupon.DoesNotExist:
                messages.warning(self.request, 'Invalid coupon code.')
                del self.request.session['coupon_code']

        total_after_discount = subtotal - discount_amount
        total_with_tax = total_after_discount + tax

        context.update({
            'total_price': subtotal,
            'tax': tax,
            'discount_amount': round(discount_amount, 2),
            'total_price_after_discount': round(total_after_discount, 2),
            'total_with_tax': round(total_with_tax, 2),
            'discount': coupon_obj.amount if coupon_obj else None,
            'discount_type': discount_type,
            'coupon': coupon_obj,
        })

        return context
