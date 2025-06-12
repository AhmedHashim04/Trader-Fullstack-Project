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
from .utils import calculate_tax
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
    tax_rate = Decimal('0.01')  # 10% tax

    def get_queryset(self):
        """Return the enhanced cart object with additional methods."""
        return ShoppingCart(self.request)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = context['cart']
        
        # Calculate pricing
        subtotal = cart.get_total_price()
        subtotal_after_discount = cart.get_total_price_after_discount()
        tax_amount = calculate_tax(subtotal_after_discount, self.tax_rate)
        cart_summary = cart.get_cart_summary()
    

        context.update({
            'subtotal': subtotal,
            'subtotal_after_discount': subtotal_after_discount,
            'cart_summary': cart_summary,
            'tax': tax_amount,
            'total_with_tax': subtotal_after_discount + tax_amount
            
        })
        return context
