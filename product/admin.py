from django.contrib import admin
from django.contrib import admin
from .models import Product, Category, Review

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'cost', 'stock', 'created_at')
    list_filter = ('created_at', 'stock')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('viewed_by',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'content', 'rating', 'created_at')
    list_filter = ('product', 'created_at')
    search_fields = ('content',)
    ordering = ('-created_at',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)

