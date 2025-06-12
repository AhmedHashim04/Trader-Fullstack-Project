from django import conf
from django.apps import config
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from product.models import Product
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.sessions.models import Session
class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(_("ID"), primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    address = models.TextField(max_length=255, verbose_name=_("Address"), blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name=_("Country"), blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"), blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    paied = models.BooleanField(_("Paied"), default=False)
    confirmed = models.BooleanField(_("Confirmed"), default=False)
    confirmation_key = models.CharField(max_length=32, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    
    def get_items(self):
        return self.items.all()

    def update_status(self, new_status):
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def get_total_price(self):
        return self.price * self.quantity
