import random
import string
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import Coupon  # عدل `yourapp` إلى اسم التطبيق الفعلي

fake = Faker()

def generate_random_code(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_random_coupon():
    discount_type = random.choice([Coupon.DiscountType.FIXED, Coupon.DiscountType.PERCENT])
    amount = Decimal(random.uniform(5, 50)).quantize(Decimal("0.01"))
    if discount_type == Coupon.DiscountType.PERCENT:
        amount = min(amount, Decimal("90.00"))  # حد أقصى للخصم المئوي
    
    coupon = Coupon.objects.create(
        code=generate_random_code(),
        name=fake.catch_phrase(),
        description=fake.text(max_nb_chars=100),
        discount_type=discount_type,
        amount=amount,
        max_discount=Decimal("100.00") if discount_type == Coupon.DiscountType.PERCENT else None,
        active=True,
        valid_from=timezone.now(),
        valid_to=timezone.now() + timedelta(days=random.randint(10, 90)),
        usage_limit=random.choice([None, random.randint(50, 500)]),
        usage_limit_per_user=random.choice([None, 1, 3, 5]),
        min_order_value=random.choice([None, Decimal("100.00"), Decimal("200.00")])
    )
    return coupon

def generate_coupons(count=10):
    coupons = []
    for _ in range(count):
        coupon = create_random_coupon()
        coupons.append(coupon)
        print(f"Created: {coupon.code}")
    return coupons
