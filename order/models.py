import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from product.models import Product


class OrderStatus(models.TextChoices):
    PENDING = 'pending', _("Pending")
    PROCESSING = 'processing', _("Processing")
    SHIPPED = 'shipped', _("Shipped")
    DELIVERED = 'delivered', _("Delivered")
    CANCELLED = 'cancelled', _("Cancelled")
    RETURNED = 'returned', _("Returned")
    FAILED = 'failed', _("Failed")


class PaymentMethod(models.TextChoices):
    COD = 'cod', _("Cash on Delivery")
    CREDIT_CARD = 'credit_card', _("Credit Card")
    VODAFONE_CASH = 'vodafone_cash', _("Vodafone Cash")
    PAYPAL = 'paypal', _("PayPal")


class ShippingMethod(models.TextChoices):
    STANDARD = 'standard', _("Standard Shipping")
    EXPRESS = 'express', _("Express Shipping")
    PICKUP = 'pickup', _("In-store Pickup")

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"

class Order(models.Model):
    id = models.UUIDField(_("ID"), primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name=_("Shipping Address"))
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    shipping_method = models.CharField(max_length=20, choices=ShippingMethod.choices, default=ShippingMethod.STANDARD)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(_("Paid"), default=False)
    coupon = models.ForeignKey('coupon.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    invoice_pdf = models.FileField(upload_to='invoices/',null=True,blank=True,verbose_name='Invoice PDF')
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def get_items(self):
        return self.items.all()

    def update_status(self, new_status):
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.save()

    def calculate_shipping_cost(self, weight: float) -> Decimal:
        if self.shipping_method == ShippingMethod.STANDARD:
            return Decimal('5.00') + Decimal(weight) * Decimal('0.50')
        elif self.shipping_method == ShippingMethod.EXPRESS:
            return Decimal('10.00') + Decimal(weight) * Decimal('1.00')
        elif self.shipping_method == ShippingMethod.PICKUP:
            return Decimal('0.00')
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        if not self.shipping_cost:
            self.shipping_cost = self.calculate_shipping_cost(weight=1.0)
        super().save(*args, **kwargs)


    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    # def get_total_price(self) -> Decimal:
    #     discount_amount = (self.price * self.quantity * self.product.discount) / 100
    #     return (self.price * self.quantity) - discount_amount

