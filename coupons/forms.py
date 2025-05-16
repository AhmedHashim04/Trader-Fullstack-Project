from django import forms
from .models import Coupon
from django.utils.translation import gettext_lazy as _

class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=8, help_text=_("Required. 8 characters or fewer. Letters, digits and @/./+/-/_ only."))
