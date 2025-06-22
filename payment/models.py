from django.db import models
from order.models import Order

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)  # from gateway
    created_at = models.DateTimeField(auto_now_add=True)

class VodafoneCashPayment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    screenshot = models.ImageField(upload_to='vodafone_cash_receipts/')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def update_order_status(self):
        self.accepted = True
        self.order.status = "paid"
        self.order.save()
    class Meta:
        verbose_name = 'Vodafone Cash Payment'
        verbose_name_plural = 'Vodafone Cash Payments'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.accepted:
            self.update_order_status()

    def __str__(self):
        return f"Vodafone Cash Payment for Order {self.order.id}"