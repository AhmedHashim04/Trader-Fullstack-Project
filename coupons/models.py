from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import Product
from django.core.validators import MaxValueValidator
from datetime import timedelta
# Create your models here.

from django.db import models
from django.utils import timezone

def get_expiry_date():
    return timezone.now() + timedelta(days=30)

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=(('fixed', 'Fixed'), ('percent', 'Percent')))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=get_expiry_date)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  
    used_count = models.PositiveIntegerField(default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and (self.usage_limit is None or self.used_count < self.usage_limit)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")
