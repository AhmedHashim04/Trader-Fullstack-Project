import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from coupon.models import Coupon, CouponUsage
from decimal import Decimal

User = get_user_model()
pytestmark = pytest.mark.django_db

@pytest.fixture
def user(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    client.login(username='testuser', password='pass')
    return user


def test_coupon_list_view(client):
    Coupon.objects.create(code="SAVE10", amount=10, active=True)
    response = client.get(reverse("coupon:coupon_list"))
    assert response.status_code == 200
    assert b"SAVE10" in response.content


def test_apply_coupon_success(client, user, mocker):
    coupon = Coupon.objects.create(code="DISCOUNT", amount=10, active=True)

    mock_cart = mocker.Mock()
    mock_cart.get_total_price_after_discount_and_tax.return_value = Decimal("100.00")
    mocker.patch("coupon.views.ShoppingCart", return_value=mock_cart)

    response = client.post(reverse("coupon:apply_coupon"), {"code": "DISCOUNT"}, follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]

    assert CouponUsage.objects.filter(user=user, coupon=coupon).exists()
    assert "Coupon \"DISCOUNT\" applied successfully!" in messages
    assert response.status_code == 200

def test_apply_coupon_expired_or_invalid(client, user, mocker):
    coupon = Coupon.objects.create(code="EXPIRED", amount=10, active=True)
    
    mock_cart = mocker.Mock()
    mock_cart.get_total_price_after_discount_and_tax.return_value = Decimal("50.00")
    mocker.patch("coupon.views.ShoppingCart", return_value=mock_cart)
    
    mocker.patch("coupon.models.Coupon.is_valid", return_value=False)

    response = client.post(reverse("coupon:apply_coupon"), {"code": "EXPIRED"}, follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    
    assert "This coupon is not valid or has expired." in messages
    assert not CouponUsage.objects.filter(user=user, coupon=coupon).exists()

def test_apply_coupon_invalid_code(client, user):
    response = client.post(reverse("coupon:apply_coupon"), {"code": "INVALID"}, follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Invalid coupon code." in messages




def test_remove_coupon(client, user):
    session = client.session
    session['coupon_id'] = 1
    session['coupon_code'] = 'SAVE20'
    session['coupon_amount'] = '20.00'
    session['coupon_discount'] = '5.00'
    session['discount_type'] = 'fixed'
    session.save()

    response = client.get(reverse("coupon:remove_coupon"), follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Coupon removed successfully." in messages
    session = client.session
    assert 'coupon_id' not in session


def test_my_coupons_view(client, user):
    coupon = Coupon.objects.create(code="USEDONE", amount=10, active=True)
    CouponUsage.objects.create(user=user, coupon=coupon, discount_amount=Decimal("5.00"))

    response = client.get(reverse("coupon:my_coupons"))
    assert response.status_code == 200
    assert b"USEDONE" in response.content
