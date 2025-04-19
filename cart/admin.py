from django.contrib import admin
from django.contrib import admin
from .models import CartModel

class CartModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created_at', 'updated_at')

admin.site.register(CartModel, CartModelAdmin)

