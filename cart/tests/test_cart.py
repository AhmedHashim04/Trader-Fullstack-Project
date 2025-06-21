import pytest
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.conf import settings
from django.core.cache import cache
from decimal import Decimal
from product.models import Product, Category
from cart.cart import Cart
from datetime import date
from django.contrib.sessions.middleware import SessionMiddleware

User = get_user_model()
pytestmark = pytest.mark.django_db

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def category():
    return Category.objects.create(name="Electronics", slug="electronics")

@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        price=Decimal("100.00"),
        discount=Decimal("10.00"),
        cost=Decimal("50.00"),
        category=category,
        description="desc"
    )


@pytest.fixture
def unauthenticated_cart(request_factory):
    
    request = request_factory.get("/")
    
    # مرر الطلب عبر middleware الجلسة
    middleware = SessionMiddleware(get_response=lambda req: None)
    middleware.process_request(request)
    request.session.save()  # لازم تتسيف عشان تاخد session_key

    request.user = type("AnonymousUser", (), {"is_authenticated": False, "id": None})()
    
    return Cart(request)

@pytest.fixture
def authenticated_cart(request_factory):
    user = User.objects.create_user(username="test", password="123")
    request = request_factory.get("/")
    request.session = {}
    request.user = user
    return Cart(request)

def test_add_product_to_cart(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=2)
    cart_data = unauthenticated_cart.cart[product.slug]
    assert cart_data["quantity"] == 2
    assert Decimal(cart_data["total_price"]) == Decimal("180.00")

def test_remove_product_from_cart(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=1)
    unauthenticated_cart.remove(product)
    assert product.slug not in unauthenticated_cart.cart

def test_clear_cart(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=1)
    unauthenticated_cart.clear()
    assert len(unauthenticated_cart.cart) == 0

def test_len_cart(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=3)
    assert len(unauthenticated_cart) == 3

def test_cart_iteration(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=2)
    items = list(iter(unauthenticated_cart))
    assert len(items) == 1
    assert items[0]['quantity'] == 2
    assert items[0]['price_after_discount'] == Decimal("90.00")

def test_get_total_price(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=2)
    assert unauthenticated_cart.get_total_price() == Decimal("200.00")

def test_get_total_discount(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=2)
    assert unauthenticated_cart.get_total_discount() == Decimal("20.00")

def test_get_total_price_after_discount(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=2)
    assert unauthenticated_cart.get_total_price_after_discount() == Decimal("180.00")

def test_get_cart_summary(unauthenticated_cart, product):
    unauthenticated_cart.add(product, quantity=1)
    summary = unauthenticated_cart.get_cart_summary()
    assert summary['total_items'] == 1
    assert summary['total_price'] == Decimal("100.00")
    assert summary['total_discount'] == Decimal("10.00")
    assert summary['total_price_after_discount'] == Decimal("90.00")
