from decimal import Decimal

def calculate_tax(subtotal: Decimal) -> Decimal:
    if subtotal >= Decimal('3000'):
        tax_rate = Decimal('0.005')  # .05% tax
    elif subtotal >= Decimal('1000'):
        tax_rate = Decimal('0.002')  # .02% tax
    else:
        tax_rate = Decimal('0.001')  # .01% tax
    """Calculate tax with precise decimal operations"""
    return tax_rate
