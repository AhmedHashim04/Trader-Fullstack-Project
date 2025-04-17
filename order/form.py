from django import forms
from .models import Order

class CompleteOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'phone_number',
            'address', 
            'city',
            'country',
            'postal_code',
            'paied',
        ]
