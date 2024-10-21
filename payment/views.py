from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import PaymentForm
from .models import Payment
from product.models import Product  

class PaymentView(LoginRequiredMixin, FormView):
    template_name = 'payment/payment.html'
    form_class = PaymentForm
    success_url = reverse_lazy('payment:success')

    def form_valid(self, form):
        amount = self.request.GET.get('amount', 0)
        product_id = self.request.GET.get('product_id')
        product = Product.objects.get(id=product_id) if product_id else None
        Payment.objects.create(
            user=self.request.user,
            product=product,
            amount=amount,
            status='completed'
        )
        return super().form_valid(form)

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'payment/payment_success.html'
