from django import forms
from .models import Order, Address

class OrderCreateForm(forms.ModelForm):
    address = forms.ModelChoiceField(
        queryset=Address.objects.all(),
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

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone_number', 'address_line', 'city', 'country', 'postal_code', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
