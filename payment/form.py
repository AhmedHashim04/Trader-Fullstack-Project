from django import forms
from .models import Payment
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['pay_phone', 'pay_image']
    
    def clean_pay_phone(self):
        pay_phone = self.cleaned_data['pay_phone']
        if not pay_phone.isdigit() or len(pay_phone) != 11:
            raise forms.ValidationError("Enter a valid 11-digit phone number.")
        if pay_phone[:4] not in ['010','011','012','015']:
            raise forms.ValidationError("Phone number must start with 010, 011, 012, or 015.")

        return pay_phone



# class PaymentForm(forms.Form):
#     card_name = forms.CharField(max_length=100, label='Name on Card')
#     card_number = forms.CharField(max_length=16, label='Card Number')
#     expiry_date = forms.CharField(max_length=5, label='Expiry Date')
#     cvv = forms.CharField(max_length=4, label='CVV')
