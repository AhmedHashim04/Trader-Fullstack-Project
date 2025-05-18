from django.contrib import admin

# Register your models here.
# admin.site.register(Variant)
from .models import Brand
from django.contrib import admin

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc')
    search_fields = ('name', 'desc')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Brand, BrandAdmin)

