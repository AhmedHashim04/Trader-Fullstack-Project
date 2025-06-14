from django import forms
from .models import Order, Address

class OrderCreateForm(forms.ModelForm):
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        label='Shipping Address',
        empty_label=None
    )

    class Meta:
        model = Order
        fields = ['address', 'payment_method', 'shipping_method']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)