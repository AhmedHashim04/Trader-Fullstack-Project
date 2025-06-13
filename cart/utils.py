from decimal import Decimal

def calculate_tax(subtotal: Decimal) -> Decimal:
    if subtotal >= Decimal('3000'):
        tax_rate = Decimal('0.005')  # .05% tax
    elif subtotal >= Decimal('1000'):
        tax_rate = Decimal('0.002')  # .02% tax
    else:
        tax_rate = Decimal('0.001')  # .01% tax
    """Calculate tax with precise decimal operations"""
    return subtotal * tax_rate

# def apply_discount(subtotal: Decimal, coupon: Coupon) -> Decimal:
#     """Apply coupon discount with type safety"""
#     if not coupon:
#         return Decimal('0.00')
        
#     if coupon.discount_type == 'percent':
#         return (subtotal * coupon.discount) / Decimal('100')
#     return min(coupon.discount, subtotal)  