from django.contrib import admin
from .models import Coupon
# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'amount', 'active', 'valid_from', 'valid_to', 'usage_limit', 'used_count', 'min_order_value')
    list_filter = ('active', 'valid_from', 'valid_to')
    search_fields = ('code',)

