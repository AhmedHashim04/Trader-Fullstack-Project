from decimal import Decimal

def calculate_tax(subtotal: Decimal, rate: Decimal) -> Decimal:
    """Calculate tax with precise decimal operations"""
    return subtotal * rate

# def apply_discount(subtotal: Decimal, coupon: Coupon) -> Decimal:
#     """Apply coupon discount with type safety"""
#     if not coupon:
#         return Decimal('0.00')
        
#     if coupon.discount_type == 'percent':
#         return (subtotal * coupon.discount) / Decimal('100')
#     return min(coupon.discount, subtotal)  