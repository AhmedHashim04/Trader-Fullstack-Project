import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.test import Client
from product.models import Product
from cart.cart import Cart

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def product():
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        price=100,
        discount=10,
        is_available=True,
        stock=10,
    )

@pytest.fixture
def client():
    return Client()


def test_cart_add_valid(client, product):
    url = reverse("cart:cart_add", args=[product.slug])
    response = client.post(url, {"quantity": 2}, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 200
    assert any("added to cart successfully" in str(m) for m in messages)


def test_cart_add_invalid_quantity(client, product):
    url = reverse("cart:cart_add", args=[product.slug])
    response = client.post(url, {"quantity": 0}, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert any("Invalid quantity specified" in str(m) for m in messages)


def test_cart_add_unavailable_product(client, product):
    product.is_available = False
    product.save()
    url = reverse("cart:cart_add", args=[product.slug])
    response = client.post(url, {"quantity": 1}, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert any("is currently unavailable" in str(m) for m in messages)


def test_cart_remove(client, product):
    url_add = reverse("cart:cart_add", args=[product.slug])
    client.post(url_add, {"quantity": 1})
    url_remove = reverse("cart:cart_remove", args=[product.slug])
    response = client.post(url_remove, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert any("removed from cart successfully" in str(m) for m in messages)


def test_cart_clear(client, product):
    url_add = reverse("cart:cart_add", args=[product.slug])
    client.post(url_add, {"quantity": 1})
    url_clear = reverse("cart:cart_clear")
    response = client.post(url_clear, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert any("Cart cleared successfully" in str(m) for m in messages)


def test_cart_view(client, product):
    url_add = reverse("cart:cart_add", args=[product.slug])
    client.post(url_add, {"quantity": 1})
    url = reverse("cart:cart_list")
    response = client.get(url)
    assert response.status_code == 200
    assert 'cart_summary' in response.context
