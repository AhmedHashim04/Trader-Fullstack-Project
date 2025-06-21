import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User
from order.models import Order, OrderItem, Address, OrderStatus, PaymentMethod, ShippingMethod
from product.models import Product
from coupon.models import Coupon


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass")


@pytest.fixture
def address(user):
    return Address.objects.create(
        user=user,
        full_name="John Doe",
        phone_number="123456789",
        address_line="123 Street",
        city="Cairo",
        country="Egypt",
        postal_code="12345",
        is_default=True
    )


@pytest.fixture
def product():
    return Product.objects.create(
        name="Test Product",
        price=Decimal("100.00"),
        cost=Decimal("80.00"),
        description="Test desc"
    )


@pytest.mark.django_db
def test_create_order(user, address):
    order = Order.objects.create(user=user, address=address)
    assert order.status == OrderStatus.PENDING
    assert order.payment_method == PaymentMethod.COD
    assert order.shipping_method == ShippingMethod.STANDARD
    assert isinstance(order.shipping_cost, Decimal)
    assert order.total_price == Decimal("0.00")


@pytest.mark.django_db
def test_order_str(user, address):
    order = Order.objects.create(user=user, address=address)
    assert str(order) == f"Order {order.id} - {user.username}"


@pytest.mark.django_db
def test_update_order_status(user, address):
    order = Order.objects.create(user=user, address=address)
    order.update_status(OrderStatus.SHIPPED)
    order.refresh_from_db()
    assert order.status == OrderStatus.SHIPPED
    assert order.status_changed_at is not None


@pytest.mark.django_db
def test_calculate_shipping_cost_standard(user, address):
    order = Order.objects.create(user=user, address=address, shipping_method=ShippingMethod.STANDARD)
    cost = order.calculate_shipping_cost(2.0)
    assert cost == Decimal("6.00")


@pytest.mark.django_db
def test_calculate_shipping_cost_express(user, address):
    order = Order.objects.create(user=user, address=address, shipping_method=ShippingMethod.EXPRESS)
    cost = order.calculate_shipping_cost(3.0)
    assert cost == Decimal("13.00")


@pytest.mark.django_db
def test_calculate_shipping_cost_pickup(user, address):
    order = Order.objects.create(user=user, address=address, shipping_method=ShippingMethod.PICKUP)
    cost = order.calculate_shipping_cost(10.0)
    assert cost == Decimal("0.00")


@pytest.mark.django_db
def test_order_item_str(user, address, product):
    order = Order.objects.create(user=user, address=address)
    item = OrderItem.objects.create(order=order, product=product, quantity=2, price=Decimal("120.00"))
    assert str(item) == f"2 x {product.name} in Order {order.id}"


@pytest.mark.django_db
def test_order_get_items(user, address, product):
    order = Order.objects.create(user=user, address=address)
    OrderItem.objects.create(order=order, product=product, quantity=1, price=Decimal("100.00"))
    OrderItem.objects.create(order=order, product=product, quantity=2, price=Decimal("200.00"))
    items = order.get_items()
    assert items.count() == 2
