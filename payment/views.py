from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import PaymentForm
from .models import Payment
from django.shortcuts import redirect, get_object_or_404 , render
from order.models import Order
from django.contrib import messages

# class PaymentView(LoginRequiredMixin, FormView):
#     template_name = 'payment/payment.html'
#     form_class = PaymentForm
#     success_url = reverse_lazy('payment:success')

#     def form_valid(self, form):
#         amount = self.request.GET.get('amount', 0)
#         product_id = self.request.GET.get('product_id')
#         product = Product.objects.get(id=product_id) if product_id else None
#         Payment.objects.create(
#             user=self.request.user,
#             product=product,
#             amount=amount,
#             status='completed'
#         )
#         return super().form_valid(form)

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'payment/payment_success.html'

def pay_by_vodafone(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            order_pay = form.save(commit=False)
            order_pay.order = order
            order.paied = True
            order_pay.save()
            order.save()  # Save the order to persist changes
            return redirect('payment:success_payment', order.id)
        else:
            messages.error(request, "Payment form is not valid.")
    else:
        form = PaymentForm()
    return render(request, 'payment/payment.html', {'form': form, 'order': order})
