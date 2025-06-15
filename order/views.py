from decimal import Decimal
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import AddressForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from cart.cart import Cart
from .models import Order, OrderItem, Address
from .forms import OrderCreateForm
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.urls import reverse
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
    success_url = reverse_lazy('order:order_list')

    def form_valid(self, form):
        cart = Cart(self.request)
        if not cart:
            form.add_error(None, 'Your cart is empty.')
            return super().form_invalid(form)

        order = form.save(commit=False)
        order.user = self.request.user
        # calculate shipping cost
        order.shipping_cost = order.calculate_shipping_cost(weight=1)
        # apply discount and tax from cart
        discount = cart.get_total_discount() or Decimal('0.00')
        tax = cart.get_tax() or Decimal('0.00')
        # compute subtotal of items
        items_total = sum(item['price'] * item['quantity'] for item in cart)
        order.total_price = (items_total + order.shipping_cost + tax - discount).quantize(Decimal('0.01'))
        order.save()

        # create order items
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'], price=item['price'])

        cart.clear()
        return super().form_valid(form)


class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = Order.objects.filter(pk=pk, user=request.user).first()
        if order and hasattr(order, 'status'):
            order.update_status('cancelled')
        return HttpResponseRedirect(reverse('order:order_detail', args=[order.pk]))


@login_required
def address_list_create_view(request):
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.save()
            return redirect('order:address')

    return render(request, 'order/address_list_create.html', {
        'form': form,
        'addresses': addresses,
    })