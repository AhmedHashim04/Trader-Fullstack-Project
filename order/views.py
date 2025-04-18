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
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.core.cache import cache


# def confirm_order(request, confirmation_key,form):
    
#         order = get_object_or_404(Order, confirmation_key=confirmation_key)
#         if order:
#             order.confirmed = True
#             order.confirmation_key = ''
#             complete_order = complete_order(request, form)

#             order.save()
#             messages.success(request, 'Order Had Confirmed Successfuly !')
#         else:
#             messages.error(request, 'Confirmed Failed , Invalid key !')
#         reverse('order:order_detail', args=[order.id])

def create_order(request):
    cart = cart_branch(request)
    if not cart.cart:
        messages.warning(request, 'Your shopping cart is empty!')
        return redirect('cart:cart_list')

    if request.method == 'POST':
        form = CompleteOrderForm(request.POST)
        if form.is_valid():
            # Send confirmation email first
            return send_order_email(request, request.user, form)
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
        

    return render(request, 'order/create_order.html', {"form": form})

def send_order_email(request, user, form):
    try:
        # Generate unique confirmation key
        confirmation_key = uuid.uuid4().hex
        
        # Store form data in session
        request.session['pending_order'] = {
            'confirmation_key': confirmation_key,
            'form_data': form.cleaned_data
        }

        # Build confirmation URL
        confirm_url = request.build_absolute_uri(
            reverse('order:confirm_order', args=[confirmation_key])
        )
        
        # Prepare email content
        subject = 'Order Confirmation Required'
        message = f'''
        Thank you for your order!
        
        Please click the following link to confirm your order:
        {confirm_url}
        
        This link will expire in 24 hours.
        '''
        
        # For development, just print the email
        print(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
        )

        messages.success(request, 'Please check your email to confirm your order.')
        return redirect('order:order_list')

    except Exception as e:
        print(f"Failed to send order confirmation email: {str(e)}")
        messages.error(request, 'Failed to send confirmation email. Please try again.')
        return redirect('cart:cart_list')



def confirm_order(request, confirmation_key):
    # Check cache for pending order
    cache_key = f"pending_order_{confirmation_key}"
    pending_order = cache.get(cache_key)

    if not pending_order:
        messages.error(request, 'Invalid or expired confirmation link.')
        return redirect('cart:cart_list')

    try:
        # Create form instance with stored data
        form = CompleteOrderForm(pending_order['form_data'])
        if form.is_valid():
            # Create the order
            order = complete_order(request, form)
            if order:
                # Clear pending order from cache
                cache.delete(cache_key)
                messages.success(request, 'Order confirmed successfully!')
                return redirect('order:order_detail', order.id)

        messages.error(request, 'Failed to create order. Please try again.')
        return redirect('cart:cart_list')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('cart:cart_list')

@login_required
@transaction.atomic
def complete_order(request, form):
    cart = cart_branch(request)
    if not cart:
        messages.warning(request, 'Your shopping cart is empty!')
        return redirect('cart:cart_list')
    
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
                paied=form.cleaned_data['paied'],
                confirmed=True
            )

            for item in cart:
                product = item['product']
                quantity = item['quantity']
                if quantity > product.stock and quantity >= 1:
                    raise ValueError(f'The requested quantity of {product.name} is not available. The available quantity is {product.stock}.')
                
                price = product.price * quantity
                order_item = OrderItem(order=order, product=product, quantity=quantity, price=price)
                order_items.append(order_item)
                total_price += price
                
                product.stock -= quantity
                product.save()
                
            if total_price >= 1:
                OrderItem.objects.bulk_create(order_items)
            
            order.total_price = total_price
            order.save()
            cart.clear()
            
            return order
    
    except ValueError as e:
        messages.error(request, str(e))
        return None
    except Exception as e:
        messages.error(request, 'An error occurred while creating the order. Please try again.')
        return None

@login_required
@transaction.atomic
def clear_order_history(request):
    try:
        Order.objects.filter(user=request.user).delete()
        messages.success(request, 'Order history cleared successfully!')
    except Exception as e:
        messages.error(request, 'An error occurred while clearing the order history. Please try again.')
    
    return redirect('order:order_list')


    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, confirmed=True).order_by('-created_at')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        cache_key = f"order_list_{self.request.user.id}"
        print(cache_key)
        orders = cache.get(cache_key)


        if not orders:
            orders = Order.objects.filter(user=self.request.user, confirmed=True).order_by('-created_at')
            cache.set(cache_key, orders, timeout=60 * 15)  # Cache for 15 minutes

        return orders


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'id'
    slug_field = 'id'

    def get_queryset(self):
        cache_key = f"order_detail_{self.request.user.id}_{self.kwargs['id']}"
        order = cache.get(cache_key)

        if not order:
            order = Order.objects.filter(user=self.request.user, id=self.kwargs['id']).first()
            cache.set(cache_key, order, timeout=60 * 15)  # Cache for 15 minutes

        return Order.objects.filter(id=order.id) if order else Order.objects.none()
