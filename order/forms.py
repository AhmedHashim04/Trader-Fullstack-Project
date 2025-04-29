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
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            for field in self.Meta.fields:
                self.fields[field].required = True
                self.fields[field].initial = getattr(user.profile, field, None)

