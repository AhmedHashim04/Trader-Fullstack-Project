from decimal import Decimal
from cart.models import Coupon

def calculate_tax(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    """Calculate tax amount based on subtotal and tax rate."""
    return subtotal * tax_rate

def apply_discount(subtotal: Decimal, coupon: Coupon) -> Decimal:
    """Apply coupon discount to subtotal."""
    if coupon.discount_type == 'percent':
        return subtotal * (coupon.amount / Decimal('100'))
    return Decimal(str(coupon.amount))