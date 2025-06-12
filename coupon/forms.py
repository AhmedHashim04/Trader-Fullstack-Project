from django import forms
from .models import Coupon

class CouponApplyForm(forms.Form):
    code = forms.CharField(
        label='Coupon Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        })
    )

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }