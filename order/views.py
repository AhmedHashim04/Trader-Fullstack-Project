from decimal import Decimal
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import AddressForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from cart.cart import Cart
from .models import Order, OrderItem, Address ,OrderStatus
from .forms import OrderCreateForm
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from coupon.models import Coupon
from coupon.views import remove_coupon
from payment.forms import PaymentProofForm
from payment.models import VodafoneCashPayment
from django.conf import settings

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

    def get_payment_status(self, order):
        """Determine if payment form should be shown."""
        has_payment = VodafoneCashPayment.objects.filter(order=order).exists()
        is_vodafone_cash = order.payment_method and order.payment_method.lower() == "vodafone_cash"
        print(is_vodafone_cash,has_payment)
        return not has_payment and is_vodafone_cash

    def get_vodafone_number(self):
        """Return Vodafone number from settings or fallback."""
        return getattr(settings, "VODAFONE_CASH_NUMBER", "01012345678")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        show_payment_form = self.get_payment_status(order)

        context.update({
            "form": PaymentProofForm(instance=order) if show_payment_form else None,
            "vodafone_number": self.get_vodafone_number() if show_payment_form else None,
            "show_payment_form": show_payment_form,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        order = self.object
        show_payment_form = self.get_payment_status(order)

        if not show_payment_form:
            messages.info(request, "Payment proof is not required or already submitted for this order.")
            return redirect(reverse("order:order_detail", kwargs={"pk": order.pk}))

        form = PaymentProofForm(request.POST, request.FILES, instance=order)

        if form.is_valid():
            # Save order with proof
            form.save()

            # Create VodafoneCashPayment record
            VodafoneCashPayment.objects.create(
                order=order,
                transaction_id=form.cleaned_data.get('transaction_id'),
                screenshot=form.cleaned_data.get('screenshot')
            )

            # Update order status
            order.status = OrderStatus.PROCESSING
            order.save()

            messages.success(request, "Payment proof submitted successfully. Your order is now being processed.")
            return redirect(reverse("order:order_detail", kwargs={"pk": order.pk}))
        
        messages.error(request, "There was an error with your payment proof. Please check the details and try again.")
        
        context = {
            "order": order,
            "form": form,
            "vodafone_number": self.get_vodafone_number() if show_payment_form else None,
            "show_payment_form": show_payment_form,
        }
        return render(request, self.template_name, context)

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
        print(discount)
        tax = cart.get_tax() or Decimal('0.00')
        # compute subtotal of items
        if self.request.session.get('coupon_discount'):
            discount += Decimal(self.request.session['coupon_discount'])
            order.coupon = Coupon.objects.get(code=self.request.session.get('coupon_code', None))
        items_total = sum(item['price'] * item['quantity'] for item in cart)

        order.total_price = (items_total + order.shipping_cost + tax - discount).quantize(Decimal('0.01'))
        if order.total_price < 0:order.total_price = 0
        order.save()
        remove_coupon(self.request)

        # create order items
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'], price=item['price'])

        cart.clear()
        messages.success(self.request, 'Your order has been placed successfully. Order Status email has been sent to you.')
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        return context


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