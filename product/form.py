from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
        
        class Meta:
            model = Review
            fields = ["REVcontent", "REVrating"]
            widgets = {
                'REVrating': forms.RadioSelect(choices=[
                    (5, '★'),
                    (4, '★'),
                    (3, '★'),
                    (2, '★'),
                    (1, '★')
                ]),
            }
             
