from django import forms
from .models import Order
from account.models import Profile



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

    
