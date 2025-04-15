from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
        
        class Meta:
            model = Review
            fields = ["content", "rating"]
            widgets = {
                'rating': forms.RadioSelect(choices=[
                    (5, '★'),
                    (4, '★'),
                    (3, '★'),
                    (2, '★'),
                    (1, '★')
                ]),
            }
             
