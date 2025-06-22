from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_joined', 'phone_number')
    search_fields = ( 'name', 'phone_number', 'city', 'country')
    ordering = ('-date_joined',)

admin.site.register(Profile, ProfileAdmin)



# make best customize for these model in admin dashboard