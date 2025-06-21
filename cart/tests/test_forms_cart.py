import pytest
from cart.forms import CartAddProductForm


@pytest.mark.parametrize("quantity, expected_valid", [
    (1, True),   # أقل كمية مسموح بها
    (5, True),   # كمية صحيحة
    (0, False),  # أقل من الحد الأدنى
    (-3, False), # سالب
    (None, False),  # مفيش قيمة
])
def test_quantity_validation(quantity, expected_valid):
    form = CartAddProductForm(data={"quantity": quantity})
    assert form.is_valid() == expected_valid


def test_update_field_default_false():
    form = CartAddProductForm(data={"quantity": 1})
    form.is_valid()
    assert form.cleaned_data["update"] is False


def test_update_field_true():
    form = CartAddProductForm(data={"quantity": 2, "update": True})
    assert form.is_valid()
    assert form.cleaned_data["update"] is True


def test_form_fields():
    form = CartAddProductForm()
    assert "quantity" in form.fields
    assert "update" in form.fields
    assert form.fields["update"].initial is False
    assert form.fields["update"].widget.__class__.__name__ == "HiddenInput"
    assert form.fields["quantity"].widget.__class__.__name__ == "NumberInput"
