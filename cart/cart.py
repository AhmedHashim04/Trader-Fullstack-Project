from django.conf import settings
from product.models import Product
from decimal import Decimal
from django.utils import timezone
from coupons.models import Coupon


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID, {})
        if settings.CART_SESSION_ID not in self.session:
            self.session[settings.CART_SESSION_ID] = self.cart
    def add(self, product, quantity=1, override_quantity=False):
        product_slug = product.slug
        if product_slug not in self.cart:
            self.cart[product_slug] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_slug]['quantity'] = quantity
        else:
            self.cart[product_slug]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_slug = product.slug
        if product_slug in self.cart:
            del self.cart[product_slug]
            self.save()

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.cart = {}
        self.save()
    @property
    def coupon(self):
        """Return the coupon model if a coupon is applied."""
        if self.coupon_id:
            try:
                return Coupon.objects.get(code=self.coupon_id, active=True)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self, coupon_code):
        """Get the discount for the given coupon code."""
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                return coupon.discount
            except Coupon.DoesNotExist:
                return 0
        elif self.coupon:
            return self.coupon.discount
        return 0

    def get_total_price_after_discount(self) -> Decimal:
        """Get the total price of the items in the cart after the discount if any."""
        if self.coupon:
            return self.get_total_price() * (1 - self.coupon.discount / 100)
        return self.get_total_price()

    def __iter__(self):
        product_slugs = self.cart.keys()
        products = Product.objects.filter(slug__in=product_slugs)
        for product in products:
            cart_item = self.cart[product.slug]
            yield {
                'product': product,
                'quantity': cart_item['quantity'],
                'price': Decimal(cart_item['price']),
                'get_total_price': Decimal(cart_item['price']) * cart_item['quantity']
            }

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True