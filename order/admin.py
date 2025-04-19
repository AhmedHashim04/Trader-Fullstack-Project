from django.contrib import admin
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_first_name', 'get_last_name', 'get_email', 'address', 'city', 'paied', 'created_at', 'updated_at']
    list_filter = ['paied', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    @admin.display(description=_('First name'))
    def get_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description=_('Last name'))
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(description=_('Email'))
    def get_email(self, obj):
        return obj.user.email

admin.site.register(Order, OrderAdmin)








