from django.contrib import admin
from features.admin import ProductImageInline
from .models import Product, Category, Review, Tag
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from features.models import Collection
import csv

@admin.action(description=_('Export selected products to CSV'))
def export_products_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name_plural}.csv'
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]

    # Write header
    writer.writerow([field.verbose_name for field in fields])

    # Write data rows
    for obj in queryset.select_related():
        data_row = []
        for field in fields:
            value = getattr(obj, field.name, '')
            if callable(value):
                value = value()
            if isinstance(value, bool):
                value = _(str(value))
            if value is None:
                value = ''
            data_row.append(str(value))
        writer.writerow(data_row)
    return response

class ProductInline(admin.TabularInline):
    model = Collection.products.through
    extra = 1
    verbose_name = _("Collection Product")
    verbose_name_plural = _("Collection Products")
    autocomplete_fields = ['collection', 'product']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductInline]
    list_display = ('name', 'price', 'cost', 'profit', 'stock', 'created_at')
    list_filter = ('created_at', 'stock', 'category')
    search_fields = ('name', 'description', 'category__name')
    ordering = ('-created_at',)
    raw_id_fields = ('viewed_by',)
    actions = [export_products_to_csv]
    list_select_related = ('category',)

    @admin.display(description=_('Profit'))
    def profit(self, obj):
        return obj.price - obj.cost



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'content', 'rating', 'created_at')
    list_filter = ('product', 'created_at', 'rating')
    search_fields = ('content', 'user__username', 'product__name')
    ordering = ('-created_at',)
    autocomplete_fields = ['product', 'user']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
