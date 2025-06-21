import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from order.models import Order, Address, OrderItem
from product.models import Product, Category
from coupon.models import Coupon
from cart.cart import Cart
from decimal import Decimal
from django.test import Client
from django.contrib.messages import get_messages
from django.core import mail


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='12345', email="test@example.com")


@pytest.fixture
def another_user(db):
    return User.objects.create_user(username='anotheruser', password='12345')


@pytest.fixture
def category(db):
    return Category.objects.create(name="Phones", slug="phones")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="iPhone",
        category=category,
        price=1000,
        cost=700,
        description="..."
    )


@pytest.fixture
def coupon(db):
    return Coupon.objects.create(code="DISCOUNT10", amount=10)


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


@pytest.fixture
def order(user, address):
    return Order.objects.create(user=user, address=address, total_price=100, shipping_cost=10)


@pytest.mark.django_db
def test_order_list_view_authenticated(client, user, order):
    client.force_login(user)
    response = client.get(reverse("order:order_list"))
    assert response.status_code == 200
    assert order in response.context["orders"]


@pytest.mark.django_db
def test_order_detail_view_authenticated(client, user, order):
    client.force_login(user)
    response = client.get(reverse("order:order_detail", args=[order.pk]))
    assert response.status_code == 200
    assert response.context["order"] == order


# @pytest.mark.django_db
# def test_order_create_success(client, user, product, coupon):
#     client.force_login(user)
#     session = client.session
#     session["cart"] = {
#         str(product.id): {
#             "quantity": 2,
#             "price": str(product.price),
#             "product_id": product.id
#         }
#     }
#     session["coupon_discount"] = "10.00"
#     session["coupon_code"] = coupon.code
#     session.save()

#     addr = Address.objects.create(user=user, full_name="Ahmed", phone_number="010", address_line="Street", city="Cairo", country="EG", postal_code="12345", is_default=True)

#     data = {
#         "address": addr.id,
#         "payment_method": "cod",
#         "shipping_method": "standard"
#     }
#     response = client.post(reverse("order:create_order"), data, follow=True)
#     assert response.status_code == 200
#     messages = [m.message for m in get_messages(response.wsgi_request)]
#     assert any("order" in msg.lower() and "placed" in msg.lower() for msg in messages), messages
#     assert Order.objects.filter(user=user).exists()
#     assert OrderItem.objects.count() == 1

    # ✅ Signal sent email
    # assert len(mail.outbox) >= 1
    # assert f"Your order" in mail.outbox[0].subject


@pytest.mark.django_db
def test_order_cancel_view(client, user, order):
    client.force_login(user)
    response = client.post(reverse("order:cancel_order", args=[order.pk]), follow=True)
    order.refresh_from_db()
    assert response.status_code == 200
    assert order.status == "cancelled"


@pytest.mark.django_db
def test_order_create_view_empty_cart(client, user):
    client.force_login(user)
    session = client.session
    session["cart"] = {}
    session.save()
    response = client.post(reverse("order:create_order"))
    assert response.status_code == 200
    form = response.context["form"]
    assert form is not None
    assert form.errors or form.non_field_errors()  # Ensure form is invalid


@pytest.mark.django_db
def test_address_list_create_view(client, user):
    client.force_login(user)
    data = {
        "full_name": "Ali",
        "phone_number": "010",
        "address_line": "Some Street",
        "city": "Giza",
        "country": "EG",
        "postal_code": "11111",
        "is_default": True
    }
    response = client.post(reverse("order:address"), data)
    assert response.status_code == 302
    assert Address.objects.filter(user=user).count() == 1
    assert Address.objects.first().is_default is True


# @pytest.mark.django_db
# def test_order_status_update_signal_sends_email(order):
#     order.status = "shipped"
#     order.save()
#     assert len(mail.outbox) >= 1
#     assert f"status updated" in mail.outbox[-1].subject
