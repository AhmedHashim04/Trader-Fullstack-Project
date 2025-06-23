from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from product.models import Product
from typing import Iterator, Dict, Any
from .utils import calculate_tax
class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.session_id = settings.CART_SESSION_ID
        self.cart = self._get_or_create_cart()
        
    def _get_or_create_cart(self):
        if self.request.user.is_authenticated:
            cache_key = f"cart_user_{self.request.user.id}"
            cart = cache.get(cache_key)
        else:
            cache_key = f"cart_session_{self.session.session_key}"
            cart = cache.get(cache_key)
        
        if cart is None:
            cart = self.session.get(self.session_id, {})
            if not isinstance(cart, dict):
                cart = {}

            if self.request.user.is_authenticated:
                cache_key = f"cart_user_{self.request.user.id}"
            else:
                cache_key = f"cart_session_{self.session.session_key}"
                
            cache.set(cache_key, cart, timeout=3600)
            
        return cart

    def add(self, product: Product, quantity: int = 1) -> None:
        if quantity <= 0:
            self.remove(product)
            return

        product_slug = str(product.slug)
        
        if product_slug not in self.cart:
            self.cart[product_slug] = {
                'quantity': 0,
                'price': str(product.price),
                'discount': str(product.discount),
                'price_after_discount': str(product.price_after_discount),
                'added_at': timezone.now().isoformat(),
                'total_price': '0'
            }

        self.cart[product_slug]['quantity'] = quantity


        # FIX: Use Decimal for money calculations
        price_after_discount = Decimal(self.cart[product_slug]['price_after_discount'])
        total_price = price_after_discount * quantity
        self.cart[product_slug]['total_price'] = str(total_price)
        
        self.save()

    def remove(self, product: Product) -> None:
        product_slug = str(product.slug)
        if product_slug in self.cart:
            del self.cart[product_slug]
            self.save()

    def clear(self) -> None:
        self.cart = {}
        self.save(clear=True)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        product_slugs = list(self.cart.keys())
        products = Product.objects.filter(slug__in=product_slugs).select_related('category')
        products_map = {str(p.slug): p for p in products}
        
        for slug, item in self.cart.items():
            product = products_map.get(slug)
            if not product:
                continue
                
            discount_amount = (Decimal(item['price']) * Decimal(item['discount']) / 100)
            
            yield {
                'product': product,
                'quantity': item['quantity'],
                'price': Decimal(item['price']),
                'discount': discount_amount,
                'price_after_discount': Decimal(item['price_after_discount']),
                'added_at': item.get('added_at'),
                'total_price': Decimal(item['total_price']),
            }

    def __len__(self) -> int:
        return sum(item['quantity'] for item in self.cart.values())

    def save(self, clear: bool = False) -> None:
        self.session[self.session_id] = self.cart
        self.session.modified = True
        
        if self.request.user.is_authenticated:
            cache_key = f"cart_user_{self.request.user.id}"
        else:
            cache_key = f"cart_session_{self.session.session_key}"
            
        if clear:
            cache.delete(cache_key)
        else:
            cache.set(cache_key, self.cart, timeout=3600)

    # FIX: Remove get_weight() - not implemented
    # FIX: Tax calculation should be external
    def get_tax(self):
        return calculate_tax(self.get_total_price_after_discount())

    def get_total_price(self) -> Decimal:
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_total_discount(self) -> Decimal:
        return sum(
            (Decimal(item['price']) * item['quantity']) * 
            (Decimal(item['discount']) / 100)
            for item in self.cart.values()
        )

    def get_total_price_after_discount(self) -> Decimal:
        return self.get_total_price() - self.get_total_discount()

    def get_total_price_after_discount_and_tax(self) -> Decimal:
        return (self.get_total_price_after_discount() * self.get_tax()) + self.get_total_price_after_discount()

    def get_cart_summary(self) -> Dict[str, Any]:
        total_price_after_discount = self.get_total_price_after_discount()
        tax_amount = (self.get_tax()*total_price_after_discount)
        total_price_after_discount_and_tax = total_price_after_discount + tax_amount
        
        return {
            'total_items': len(self),
            'total_price': self.get_total_price(),
            'total_discount': self.get_total_discount(),
            'total_price_after_discount': total_price_after_discount,
            'tax_amount': tax_amount,
            'total_price_after_discount_and_tax': total_price_after_discount_and_tax
        }
    
    @staticmethod
    def merge_on_login(user, old_session_key) -> int:
        session_cart_key = f"cart_session_{old_session_key}"
        user_cart_key = f"cart_user_{user.id}"

        session_cart = cache.get(session_cart_key, {})
        user_cart = cache.get(user_cart_key, {})

        merged_cart = user_cart.copy()
        added_count = 0

        for product_id, item in session_cart.items():
            try:
                product = Product.objects.get(slug=product_id)
            except Product.DoesNotExist:
                continue

            new_quantity = item['quantity']
            if product_id in merged_cart:
                new_quantity += merged_cart[product_id]['quantity']

            if new_quantity > product.stock:
                continue

            merged_cart[product_id] = item.copy()
            merged_cart[product_id]['quantity'] = new_quantity
            added_count += 1

        cache.set(user_cart_key, merged_cart, timeout=3600)
        cache.delete(session_cart_key)
        
        return added_count
