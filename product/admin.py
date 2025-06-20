from django.contrib import admin
from features.admin import ProductImageInline
from .models import Product, Category, Review, Tag
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from features.models import Collection
import csv



def export_products_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name}.csv'
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, bool):
                value = _(str(value))
            data_row.append(value)
        writer.writerow(data_row)

    return response

export_products_to_csv.short_description = _('Export selected products to CSV')
class ProductInline(admin.TabularInline):
    model = Collection.products.through  # Assuming ManyToManyField
    extra = 1
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductInline]
    list_display = ('name', 'price', 'cost', 'profit', 'stock', 'created_at')
    list_filter = ('created_at', 'stock')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('viewed_by',)
    actions = [export_products_to_csv]

    def profit(self, obj):
        return obj.price - obj.cost
    profit.short_description = 'Profit'

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
admin.site.register(Tag, admin.ModelAdmin)


