from django.conf import settings
from django.db import models
from product.models import Product
from decimal import Decimal

class Cart(models.Model):
    def  __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product):
        product_id = product.PRDslug
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 1, 'price': float(product.PRDprice)}
        self.save()

    def update(self, product, quantity):
        product_id = product.PRDslug
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
        self.save()

    def remove(self, product):
        product_id = str(product.PRDslug)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()
        

    def get_total_price(self):
        return sum(float(item['price']) * int(item['quantity']) for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
        
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(PRDslug__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.PRDslug)]['product'] = product
        for item in cart.values():
            item['price'] = float(item['price'])
            item['quantity'] = int(item['quantity'])
            item['total'] = float(item['price']) * int(item['quantity'])
            yield item

    # def __len__(self):
    #     return sum((item['quantity']) for item in self.cart.values())
    
    def save(self):
        self.session.modified = True