import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from coupon.models import Coupon, CouponUsage
from datetime import timedelta

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="123")


@pytest.fixture
def coupon():
    return Coupon.objects.create(
        code="SAVE10",
        discount_type=Coupon.DiscountType.PERCENT,
        amount=10,
        active=True,
        valid_from=timezone.now() - timedelta(days=1),
        valid_to=timezone.now() + timedelta(days=1),
        usage_limit=5,
        usage_limit_per_user=2,
        min_order_value=50
    )


def test_coupon_valid_basic(coupon):
    assert coupon.is_valid(cart_total=Decimal("100.00")) is True


def test_coupon_invalid_due_to_date(coupon):
    coupon.valid_from = timezone.now() + timedelta(days=1)
    coupon.save()
    assert coupon.is_valid(cart_total=Decimal("100.00")) is False


def test_coupon_invalid_due_to_usage_limit(coupon):
    coupon.used_count = 5
    coupon.save()
    assert coupon.is_valid(cart_total=Decimal("100.00")) is False


def test_coupon_invalid_due_to_min_order(coupon):
    assert coupon.is_valid(cart_total=Decimal("10.00")) is False


def test_coupon_invalid_due_to_user_usage(coupon, user):
    for _ in range(2):
        CouponUsage.objects.create(coupon=coupon, user=user, discount_amount=5)
    assert coupon.is_valid(user=user, cart_total=Decimal("100.00")) is False


def test_apply_discount_percent_within_max(coupon):
    coupon.max_discount = Decimal("15.00")
    discount_price = coupon.apply_discount(Decimal("200.00"))
    assert discount_price == Decimal("185.00")


def test_apply_discount_percent_exceeds_max(coupon):
    coupon.max_discount = Decimal("10.00")
    discount_price = coupon.apply_discount(Decimal("200.00"))
    assert discount_price == Decimal("190.00")


def test_apply_fixed_discount():
    c = Coupon.objects.create(
        code="FIXED10",
        discount_type=Coupon.DiscountType.FIXED,
        amount=Decimal("10.00"),
        active=True,
        valid_from=timezone.now() - timedelta(days=1),
        valid_to=timezone.now() + timedelta(days=1),
    )
    discounted = c.apply_discount(Decimal("50.00"))
    assert discounted == Decimal("40.00")


def test_apply_discount_free_shipping():
    c = Coupon.objects.create(
        code="FREESHIP",
        discount_type=Coupon.DiscountType.FREE_SHIPPING,
        amount=0,
        active=True,
        valid_from=timezone.now() - timedelta(days=1),
        valid_to=timezone.now() + timedelta(days=1),
    )
    assert c.apply_discount(Decimal("100.00")) == Decimal("100.00")


def test_coupon_str_display(coupon):
    assert str(coupon) == "SAVE10 (percent: 10)"


def test_coupon_usage_str(user, coupon):
    usage = CouponUsage.objects.create(coupon=coupon, user=user, discount_amount=5)
    assert coupon.code in str(usage)
    assert str(user) in str(usage)