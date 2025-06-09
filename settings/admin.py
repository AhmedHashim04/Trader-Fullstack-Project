from .models import Product, ProductImage
from .models import Brand
from django.contrib import admin

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc')
    search_fields = ('name', 'desc')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Brand, BrandAdmin)
# admin.site.register(Variant)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # عدد الفورمات المبدئية


