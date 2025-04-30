from django.conf import settings
from product.models import Product
from decimal import Decimal


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