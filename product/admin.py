from django.contrib import admin
from .models import Product,   Category, Review #, Order, OrderItem , Alternative , ProductImage

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Review)