import pytest
from order.forms import OrderCreateForm, AddressForm
from order.models import Address, Order, PaymentMethod, ShippingMethod
from django.contrib.auth.models import User
from decimal import Decimal

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def another_user(db):
    return User.objects.create_user(username='anotheruser', password='12345')


@pytest.fixture
def address(user):
    return Address.objects.create(
        user=user,
        full_name="Ahmed Hashim",
        phone_number="0123456789",
        address_line="Nile Street",
        city="Cairo",
        country="Egypt",
        postal_code="12345",
        is_default=True
    )

@pytest.mark.django_db
def test_order_create_form_valid(user, address):
    form_data = {
        'address': address.id,
        'payment_method': PaymentMethod.CREDIT_CARD,
        'shipping_method': ShippingMethod.EXPRESS,
    }
    form = OrderCreateForm(data=form_data, user=user)
    assert form.is_valid()
    assert form.cleaned_data['address'] == address


@pytest.mark.django_db
def test_order_create_form_filters_addresses_by_user(user, address, another_user):
    other_address = Address.objects.create(
        user=another_user,
        full_name="Other User",
        phone_number="0000",
        address_line="123 Street",
        city="Alex",
        country="Egypt",
        postal_code="45678"
    )
    form = OrderCreateForm(user=user)
    assert address in form.fields['address'].queryset
    assert other_address not in form.fields['address'].queryset


@pytest.mark.django_db
def test_order_create_form_invalid_missing_fields(user):
    form = OrderCreateForm(data={}, user=user)
    assert not form.is_valid()
    assert 'address' in form.errors
    assert 'payment_method' in form.errors
    assert 'shipping_method' in form.errors


@pytest.mark.django_db
def test_address_form_valid():
    form_data = {
        'full_name': 'Ahmed Hashim',
        'phone_number': '0123456789',
        'address_line': '123 Nile St',
        'city': 'Cairo',
        'country': 'Egypt',
        'postal_code': '12345',
        'is_default': True
    }
    form = AddressForm(data=form_data)
    assert form.is_valid()
    assert form.cleaned_data['city'] == 'Cairo'


@pytest.mark.django_db
def test_address_form_invalid_missing_required():
    form = AddressForm(data={})
    assert not form.is_valid()
    required_fields = ['full_name', 'phone_number', 'address_line', 'city', 'country', 'postal_code']
    for field in required_fields:
        assert field in form.errors
