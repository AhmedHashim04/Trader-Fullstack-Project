from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db import transaction
from django.contrib import messages
from .models import Order, OrderItem
from .form import CompleteOrderForm
from django.urls import reverse
from cart.cart import Cart as cart_branch

def create_order(request):
    cart = cart_branch(request)
    
    if request.method == 'POST':
        if not cart:
            messages.warning(request, 'Your shopping cart is empty!')
            return redirect('cart:cart_list')
        
        form = CompleteOrderForm(request.POST)
        if form.is_valid():
            complete_order(request,form)

    else:
        form = CompleteOrderForm()
    return render(request,'order/create_order.html',{"form":form})


@login_required
@transaction.atomic
def complete_order(request,form):
    cart = cart_branch(request)
    if not cart:
        messages.warning(request, 'Your shopping cart is empty!')
        return redirect('cart:cart_list')
    
    total_price = 0
    order_items = []
    
    try:              

        with transaction.atomic():
            order = Order.objects.create(user=request.user, total_price=0,
                                        phone_number = form.cleaned_data['phone_number'],
                                        address = form.cleaned_data['address'],
                                        city = form.cleaned_data['city'],
                                        postal_code = form.cleaned_data['postal_code'],
                                        paied = form.cleaned_data['paied'],
                                        )

            for item in cart:
                product = item['product']
                quantity = item['quantity']
                if quantity > product.stock and quantity >=1:
                    raise ValueError(f'The requested quantity of {product.name} is not available. The available quantity is {product.stock}.')
                
                price = product.price * quantity
                order_item = OrderItem(order=order, product=product, quantity=quantity, price=price)
                order_items.append(order_item)
                total_price += price
                
                product.stock -= quantity
                product.save()
            if total_price >= 1 :
                OrderItem.objects.bulk_create(order_items)
            
            order.total_price = total_price
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
        Order.objects.filter(user=request.user).delete()
        messages.success(request, 'Order history cleared successfully!')
    except Exception as e:
        messages.error(request, 'An error occurred while clearing the order history. Please try again.')
    
    return redirect('order:order_list')

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'id'
    slug_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
