from django.shortcuts import  redirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from .models import CartModel as cartmodel
from .cart import Cart as cart_branch
from product.models import Product
from .form import CartAddProductForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

@login_required
def cart_add(request, slug ):
    cart = cart_branch(request)
    product = get_object_or_404(Product, PRDslug = slug)
    cart.add(product=product)
    messages.success(request, f'{product.PRDname} Added to Cart Successfully')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))

@login_required
def cart_remove(request, slug ):
    cart = cart_branch(request)
    product = get_object_or_404(Product, PRDslug = slug)
    cart.remove(product)
    messages.success(request, 'Product Removed Successfully')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))

@login_required
def cart_update(request, slug):
    cart = cart_branch(request)
    product = get_object_or_404(Product, PRDslug = slug)
    cart.update(product, request.POST.get('quantity'))
    messages.success(request, 'Cart Updated Successfully')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_list'))


def cart_clear(request):
    cart = cart_branch(request)
    cart.clear()
    messages.success(request, 'Cart Cleared Successfully')
    return redirect('cart:cart_list')

class CartView(LoginRequiredMixin, ListView):
    model = cartmodel
    template_name = 'cart/cart.html'
    context_object_name = 'cart'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = cart_branch(self.request)
        context['form'] = CartAddProductForm()
        context['total_price'] = context['cart'].get_total_price()
        return context
