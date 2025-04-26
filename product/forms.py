from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["content", "rating"]
        widgets = {
            'rating': forms.Select(choices=[
                (5, '★★★★★'),
                (4, '★★★★'),
                (3, '★★★'),
                (2, '★★'),
                (1, '★'),
            ]),
            #make content text area with 4 rows and default content = ""
            'content': forms.Textarea(attrs={'rows': 4}),
        }
