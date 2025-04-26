from django import forms

class EmailForm(forms.Form):
    name          = forms.CharField(max_length=25)
    from_email    = forms.EmailField()
    title         = forms.CharField(required=True , widget=forms.Textarea)
    message       = forms.CharField(required=True , widget=forms.Textarea)
    