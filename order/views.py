from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.db import transaction
from django.contrib import messages
from .models import Order, OrderItem
from .forms import CompleteOrderForm
from django.urls import reverse
from cart.cart import Cart as cart_branch
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.core.cache import cache
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import get_template
import weasyprint
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_order_pdf(request, id):
    order = get_object_or_404(Order, id=id)
    html = get_template('order/pdf.html').render({'order': order})
    pdf = weasyprint.HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="order_{order.id}.pdf"'
    return response

def create_order(request):
        cart = cart_branch(request)
        if not cart.cart:
            messages.warning(request, 'Your shopping cart is empty!')
            return redirect('cart:cart_list')

        if request.method == 'POST':
            form = CompleteOrderForm(request.POST)
            if form.is_valid():
                request.session['form_data'] = form.cleaned_data
                return redirect('order:preview_order')
        else:
            profile = request.user.profile
            form = CompleteOrderForm(initial={
                'phone_number': profile.phone_number,
                'address': profile.address,
                'city': profile.city,
                'country': profile.country,
                'postal_code': profile.postal_code,
                'paied': False,
            })

        subtotal = cart.get_total_price()

        return render(request, 'order/create_order.html', {
            "form": form,
            "cart": cart,
            "total_price": subtotal,
            "discount_amount": (cart.get_discount),
            "total_price_after_discount": (cart.get_total_price_after_discount),
        })

class PreviewView(TemplateView):
    template_name = "order/preview_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_data"] = self.request.session.get('form_data', {})
        context["cart"] = cart_branch(self.request)
        return context

    def post(self, request, *args, **kwargs):
        form_data = request.session.get('form_data')
        if not form_data:
            messages.error(request, "Form data not found.")
            return redirect('order:create_order')

        form = CompleteOrderForm(form_data)
        if form.is_valid():
            return send_order_email(request, request.user, form)

        messages.error(request, "Invalid form data.")
        return redirect('order:create_order')

class CheckoutView(TemplateView):
    """Displays the checkout confirmation page."""
    template_name = "order/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = Order.objects.filter(user=self.request.user, id=self.kwargs['id']).first()
        return context
def send_order_email(request, user, form):
    try:
        confirmation_key = uuid.uuid4().hex
        cache_key = f"pending_order_{confirmation_key}"

        # حفظ بيانات الطلب مؤقتًا
        cache.set(cache_key, {
            'confirmation_key': confirmation_key,
            'form_data': form.cleaned_data
        }, timeout=86400)  # 24 ساعة

        # رابط التأكيد
        confirm_url = request.build_absolute_uri(
            reverse('order:confirm_order', args=[confirmation_key])
        )

        subject = 'Order Confirmation Required'
        message = f'''
Thank you for your order!

Please click the following link to confirm your order:
{confirm_url}

This link will expire in 24 hours.
        '''

        # send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        print(subject, message, settings.EMAIL_HOST_USER, [user.email])  # للتجريب

        messages.success(request, 'Please check your email to confirm your order.')
        return redirect('order:order_list')

    except Exception as e:
        print(f"Failed to send order confirmation email: {str(e)}")
        messages.error(request, 'Failed to send confirmation email. Please try again.')
        return redirect('cart:cart_list')

def confirm_order(request, confirmation_key):
    cache_key = f"pending_order_{confirmation_key}"
    pending_order = cache.get(cache_key)

    if not pending_order:
        messages.error(request, 'Invalid or expired confirmation link.')
        return redirect('cart:cart_list')

    try:
        form = CompleteOrderForm(pending_order['form_data'])
        if form.is_valid():
            order = complete_order(request, form)
            if order:
                cache.delete(cache_key)
                messages.success(request, 'Order confirmed successfully!')
                return redirect('order:checkout', order.id)

        messages.error(request, 'Failed to create order. Please try again.')
        return redirect('cart:cart_list')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('cart:cart_list')

@login_required
@transaction.atomic
def complete_order(request, form):
    cart = cart_branch(request)
    if not cart.cart:
        messages.warning(request, 'Your shopping cart is empty!')
        return None

    total_price = 0
    order_items = []

    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_price=0,
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                #paied=form.cleaned_data['paied'],
                confirmed=True
            )

            for item in cart:
                product = item['product']
                quantity = item['quantity']
                if quantity > product.stock or quantity < 1:
                    raise ValueError(f'The requested quantity of {product.name} is not available. Available: {product.stock}')

                price = product.price * quantity
                order_item = OrderItem(order=order, product=product, quantity=quantity, price=price)
                order_items.append(order_item)
                total_price += price

                product.stock -= quantity
                product.save()

            if total_price >= 1:
                OrderItem.objects.bulk_create(order_items)

            order.total_price = total_price
            order.save(session_key=request.session.session_key)
            cart.clear()

            return order

    except ValueError as e:
        messages.error(request, str(e))
        return None
    except Exception as e:
        import traceback
        print("Unexpected error during order creation:", str(e))
        traceback.print_exc()  # يطبع التراك باك بالكامل في الكونسول
        messages.error(request, 'An error occurred while creating the order. Please try again.')
        return None

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # cache_key = f"order_list_{self.request.user.id}"
        # orders = cache.get(cache_key)

        # if not orders:
        orders = Order.objects.filter(user=self.request.user, confirmed=True).order_by('-created_at')
            # cache.set(cache_key, orders, timeout=60 * 15)

        return orders

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        cache_key = f"order_detail_{self.request.user.id}_{self.kwargs['id']}"
        order = cache.get(cache_key)

        if not order:
            order = Order.objects.filter(user=self.request.user, id=self.kwargs['id']).first()
            if order:
                cache.set(cache_key, order, timeout=60 * 15)

        if not order:
            return Order.objects.none()
        return Order.objects.filter(id=order.id)

@login_required
@transaction.atomic
def clear_order_history(request):
    try:
        Order.objects.filter(user=request.user).delete()
        messages.success(request, 'Order history cleared successfully!')
    except Exception as e:
        messages.error(request, 'An error occurred while clearing the order history. Please try again.')

    return redirect('order:order_list')
