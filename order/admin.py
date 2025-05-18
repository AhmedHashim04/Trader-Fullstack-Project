from django.contrib import admin
from .models import Order, OrderItem
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
import csv
from django.utils.safestring import mark_safe

def order_pdf_link(obj):
    url = reverse('order:admin_order_pdf', args=[obj.pk])
    return mark_safe(f'<a href="{url}">{_('PDF')}</a>')

order_pdf_link.short_description = _('PDF')

def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, bool):
                value = _(str(value)) # Translate boolean value
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_to_csv.short_description = _('Export to CSV')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_first_name', 'get_last_name', 'get_email', 'address', 'city', 'paied', 'created_at', 'updated_at', order_pdf_link]
    list_filter = ['paied', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

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








