from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.timezone import localtime
from .models import Order, OrderItem, Address, OrderStatus


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)
    extra = 0

    def total_price(self, obj):
        return obj.get_total_price()
    total_price.short_description = _('Total Price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'status', 'payment_method', 'total_price', 'created_at', 'status_changed_at')
    list_filter = ('status', 'payment_method', 'shipping_method', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'confirmation_key')
    readonly_fields = ('total_price', 'shipping_cost', 'created_at', 'updated_at', 'status_changed_at')
    inlines = [OrderItemInline]
    autocomplete_fields = ('user', 'address')
    list_select_related = ('user', 'address')
    actions = ['mark_as_shipped', 'mark_as_cancelled']

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = _('User')

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status=OrderStatus.SHIPPED, status_changed_at=localtime())
        self.message_user(request, _('%d order(s) marked as shipped.') % updated)
    mark_as_shipped.short_description = _('Mark selected orders as shipped')

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status=OrderStatus.CANCELLED, status_changed_at=localtime())
        self.message_user(request, _('%d order(s) marked as cancelled.') % updated)
    mark_as_cancelled.short_description = _('Mark selected orders as cancelled')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'country', 'is_default')
    list_filter = ('country', 'is_default')
    search_fields = ('full_name', 'user__username', 'address_line')
