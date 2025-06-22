from django import forms
from .models import VodafoneCashPayment
class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = VodafoneCashPayment
        fields = ['transaction_id', 'screenshot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to widgets
        self.fields['transaction_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Transaction ID',
        })
        self.fields['screenshot'].widget.attrs.update({
            'class': 'form-control',
        })

