from decimal import Decimal
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from cart.cart import Cart
from .models import Order, OrderItem, Address
from .forms import OrderCreateForm

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = 'order/create_order.html'
    success_url = reverse_lazy('order:list')

    def form_valid(self, form):
        cart = Cart(self.request)
        if not cart:
            form.add_error(None, 'Your cart is empty.')
            return super().form_invalid(form)

        order = form.save(commit=False)
        order.user = self.request.user
        # calculate shipping cost
        order.shipping_cost = order.calculate_shipping_cost(weight=cart.get_weight())
        # apply discount and tax from cart
        discount = cart.get_total_discount() or Decimal('0.00')
        tax = cart.get_tax() or Decimal('0.00')
        # compute subtotal of items
        items_total = sum(item['price'] * item['quantity'] for item in cart)
        order.total_price = (items_total + order.shipping_cost + tax - discount).quantize(Decimal('0.01'))
        order.save()

        # create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
            )
        cart.clear()
        return super().form_valid(form)
