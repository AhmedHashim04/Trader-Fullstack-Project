from django.db import models
from order.models import Order

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)  # from gateway
    created_at = models.DateTimeField(auto_now_add=True)