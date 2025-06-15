from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib import messages

from django.views.decorators.http import require_POST
from django.urls import reverse
from typing import  Dict, Any
from .cart import Cart as ShoppingCart
from product.models import Product
import logging
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

@require_POST
def cart_add(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    referer_url = request.META.get('HTTP_REFERER', reverse('cart:cart_list'))

    if not url_has_allowed_host_and_scheme(referer_url, allowed_hosts={request.get_host()}):
        referer_url = reverse('cart:cart_list')

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity specified")
        return redirect(referer_url)

    if not (product.is_available and product.is_in_stock):
        messages.warning(request, f'{product.name} is currently unavailable')
        return redirect(referer_url)
    
    # FIX: Check available stock considering current cart quantity
    current_quantity = cart.cart.get(str(product.slug), {}).get('quantity', 0)
    if quantity + current_quantity > product.stock:
        messages.warning(request, 
            f'Only {product.stock - current_quantity} additional units available for {product.name}')
        return redirect(referer_url)

    cart.add(product=product, quantity=quantity)
    messages.success(request, f'{product.name} added to cart successfully')
    return redirect(referer_url)

@require_POST
def cart_remove(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    referer_url = request.META.get('HTTP_REFERER', reverse('cart:cart_list'))
    if not url_has_allowed_host_and_scheme(referer_url, allowed_hosts={request.get_host()}):
        referer_url = reverse('cart:cart_list')
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart successfully')
    return redirect(referer_url)

@require_POST
def cart_clear(request):
    cart = ShoppingCart(request)
    cart.clear()
    messages.success(request, 'Cart cleared successfully')
    return redirect('cart:cart_list')

class CartView( ListView):
    """
    Advanced cart view with detailed pricing breakdown and coupon handling.
    """
    template_name = 'cart/cart.html'
    context_object_name = 'cart'

    def get_queryset(self):return ShoppingCart(self.request)
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = context['cart']
        cart_summary = cart.get_cart_summary()
        context.update({
            'cart_summary': cart_summary,
        })
        return context
