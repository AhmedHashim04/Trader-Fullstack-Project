from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MinValueValidator

def get_default_expiry_date():
    return timezone.now() + timedelta(days=30)

class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = 'fixed', _('Fixed Amount')
        PERCENT = 'percent', _('Percentage')
        FREE_SHIPPING = 'free_shipping', _('Free Shipping')
    
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Coupon Code"))
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Coupon Name"))
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=20,choices=DiscountType.choices,default=DiscountType.PERCENT)
    amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    max_discount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=get_default_expiry_date)
    usage_limit = models.PositiveIntegerField(null=True,blank=True,verbose_name=_("Total Usage Limit"))
    used_count = models.PositiveIntegerField(default=0)
    usage_limit_per_user = models.PositiveIntegerField(null=True,blank=True)
    min_order_value = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_valid(self, user=None, cart_total=0):
        now = timezone.now()
        valid = (
            self.active and
            self.valid_from <= now <= self.valid_to and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )
        
        if self.min_order_value and cart_total < self.min_order_value:
            valid = False
            
        if user and self.usage_limit_per_user:
            user_usage = CouponUsage.objects.filter(coupon=self, user=user).count()
            if user_usage >= self.usage_limit_per_user:
                valid = False
                
        return valid
    
    def apply_discount(self, original_price):
        if self.discount_type == self.DiscountType.FIXED:
            return max(original_price - self.amount, 0)
        elif self.discount_type == self.DiscountType.PERCENT:
            discount = original_price * (self.amount / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return max(original_price - discount, 0)
        elif self.discount_type == self.DiscountType.FREE_SHIPPING:
            return original_price  # Shipping handled separately
        return original_price
    
    def __str__(self):
        return f"{self.code} ({self.discount_type}: {self.amount})"
    
    class Meta:
        ordering = ['-created_at']


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.user} on {self.used_at}"