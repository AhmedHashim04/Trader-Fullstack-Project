from django.conf import settings
from product.models import Product
from decimal import Decimal

class Cart:
    def  __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product):
        product_slug = product.slug
        if product_slug not in self.cart:
            self.cart[product_slug] = {'quantity': 1, 'price': float(product.price)}
        self.save()

    def update(self, product, quantity):
        quantity = int(quantity)
        product_slug = product.slug
        if product_slug in self.cart:
            self.cart[product_slug]['quantity'] = quantity
        self.save()



    def remove(self, product):
        product_slug = str(product.slug)
        if product_slug in self.cart:
            del self.cart[product_slug]
        self.save()
        

    def get_total_price(self):
        return sum(
            float(item.get('price') or 0) * int(item.get('quantity') or 0)
            for item in self.cart.values()
        )
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        product_slugs = self.cart.keys()
        products = Product.objects.filter(slug__in=product_slugs)
        for product in products:
            cart_item = self.cart[str(product.slug)]
            yield {
                'product': product,
                'quantity': cart_item['quantity'],
                'price': cart_item['price'],
                'get_total_price': cart_item['price'] * cart_item['quantity']
            }
    def save(self):
        self.session.modified = True 