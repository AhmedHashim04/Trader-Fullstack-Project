from django import forms

class PaymentForm(forms.Form):
    card_name = forms.CharField(max_length=100, label='Name on Card')
    card_number = forms.CharField(max_length=16, label='Card Number')
    expiry_date = forms.CharField(max_length=5, label='Expiry Date')
    cvv = forms.CharField(max_length=4, label='CVV')
