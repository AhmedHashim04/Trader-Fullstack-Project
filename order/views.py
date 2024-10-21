from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db import transaction
from django.contrib import messages
from .models import Order, OrderItem
from django.urls import reverse
from cart.cart import Cart as cart_branch

@login_required
@transaction.atomic
def create_order(request):
    cart = cart_branch(request)
    if not cart:
        messages.warning(request, 'Your shopping cart is empty!')
        return redirect('cart:cart_list')
    
    total_price = 0
    order_items = []
    
    try:
        with transaction.atomic():
            order = Order.objects.create(ORDuser=request.user, ORDtotal_price=0)
            
            for item in cart:
                product = item['product']
                quantity = item['quantity']
                if quantity > product.PRDstock:
                    raise ValueError(f'The requested quantity of {product.PRDname} is not available. The available quantity is {product.PRDstock}.')
                
                price = product.PRDprice * quantity
                order_item = OrderItem(OITEMorder=order, OITEMproduct=product, OITEMquantity=quantity, OITEMprice=price)
                order_items.append(order_item)
                total_price += price
                
                product.PRDstock -= quantity
                product.save()
            
            OrderItem.objects.bulk_create(order_items)
            
            order.ORDtotal_price = total_price
            order.save()
            
            cart.clear()
        
        messages.success(request, 'Order created successfully!')
        return redirect('order:order_list')
    
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart:cart_list')
    except Exception as e:
        messages.error(request, 'An error occurred while creating the order. Please try again.')
        return redirect('cart:cart_list')

@login_required
@transaction.atomic
def clear_order_history(request):
    try:
        Order.objects.filter(ORDuser=request.user).delete()
        messages.success(request, 'Order history cleared successfully!')
    except Exception as e:
        messages.error(request, 'An error occurred while clearing the order history. Please try again.')
    
    return redirect('order:order_list')

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(ORDuser=self.request.user).order_by('-ORDcreated_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'slug'
    slug_field = 'ORDslug'

    def get_queryset(self):
        return Order.objects.filter(ORDuser=self.request.user)
