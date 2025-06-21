# tests/forms/test_coupon_forms.py

import pytest
from django import forms
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from coupon.forms import CouponApplyForm, CouponForm
from coupon.models import Coupon

pytestmark = pytest.mark.django_db

# ========== CouponApplyForm ==========

def test_coupon_apply_form_valid_code():
    form = CouponApplyForm(data={"code": "SUMMER2025"})
    assert form.is_valid()
    assert form.cleaned_data["code"] == "SUMMER2025"

def test_coupon_apply_form_empty_code():
    form = CouponApplyForm(data={"code": ""})
    assert not form.is_valid()
    assert "code" in form.errors


# ========== CouponForm ==========

def test_coupon_form_valid_data():
    now = timezone.now()
    form_data = {
        "code": "DISCOUNT25",
        "name": "25% Off",
        "description": "Get 25% off on orders.",
        "discount_type": "percent",
        "amount": Decimal("25.00"),
        "max_discount": Decimal("100.00"),
        "active": True,
        "valid_from": now,
        "valid_to": now + timedelta(days=10),
        "usage_limit": 100,
        "used_count": 10,
        "usage_limit_per_user": 5,
        "min_order_value": Decimal("200.00"),
    }
    form = CouponForm(data=form_data)
    assert form.is_valid()

def test_coupon_form_missing_required_fields():
    form = CouponForm(data={})
    assert not form.is_valid()
    assert "code" in form.errors
    assert "amount" in form.errors
    assert "valid_from" in form.errors
    assert "valid_to" in form.errors
    assert "discount_type" in form.errors

def test_coupon_form_negative_amount_invalid():
    now = timezone.now()
    form_data = {
        "code": "NEGATIVE",
        "amount": Decimal("-10.00"),
        "discount_type": "fixed",
        "valid_from": now,
        "valid_to": now + timedelta(days=5),
    }
    form = CouponForm(data=form_data)
    assert not form.is_valid()
    assert "amount" in form.errors

def test_coupon_form_widget_types():
    form = CouponForm()
    assert isinstance(form.fields["valid_from"].widget, forms.DateTimeInput)
    assert isinstance(form.fields["valid_to"].widget, forms.DateTimeInput)
    assert isinstance(form.fields["description"].widget, forms.Textarea)
