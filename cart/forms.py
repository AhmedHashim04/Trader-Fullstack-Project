from django import forms
class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    class Meta:
        fields = ['quantity', 'update']

