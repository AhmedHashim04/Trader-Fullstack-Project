from django.contrib import admin
from .models import Coupon, CouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'discount_type', 'amount', 'active', 'valid_from', 'valid_to', 'used_count', 'usage_limit')
    list_filter = ('active', 'discount_type')
    search_fields = ('code', 'name')
    date_hierarchy = 'valid_to'
    ordering = ('-created_at',)
    list_editable = ('active',)

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'used_at', 'discount_amount', 'order_id')
    list_filter = ('coupon', 'used_at')
    search_fields = ('coupon__code', 'user__username', 'order_id')
    date_hierarchy = 'used_at'