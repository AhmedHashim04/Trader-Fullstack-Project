from .models import  ProductImage, Collection, Brand
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


class ProductInline(admin.TabularInline):
    model = Collection.products.through  # Assuming ManyToManyField
    extra = 1


class CollectionAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ('name', 'slug', 'created_at', 'is_active')
    list_filter = ('created_at', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ('products',)  # لو في ManyToMany مباشرة في Collection


    def export_collections_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=collections.csv'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Slug', 'Created At', 'Is Active'])

        for collection in queryset:
            writer.writerow([collection.id, collection.name, collection.slug, collection.created_at, collection.is_active])

        return response

    export_collections_to_csv.short_description = "Export selected collections to CSV"

admin.site.register(Collection, CollectionAdmin)
