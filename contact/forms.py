from django import forms

from django.core.validators import RegexValidator

class EmailForm(forms.Form):
    name = forms.CharField(
        max_length=25,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+(?:\s+[a-zA-Z]+)*$',
                message='Name should only contain letters and spaces'
            )
        ]
    )

    from_email = forms.EmailField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$',
                message='Invalid email address'
            )
        ]
    )

    title = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 1, 'placeholder': 'Subject'})
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message'})
    )
