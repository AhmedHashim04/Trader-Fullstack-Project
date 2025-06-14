from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
from typing import Dict, Any, Iterator
from product.models import Product
import logging
logger = logging.getLogger(__name__)


class Cart:
    """
    Advanced shopping cart implementation with caching, type hints, and performance optimizations.
    """
    def __init__(self, request):
        """
        Initialize the cart with session and caching support.
        """
        self.request = request
        self.session = request.session
        self.session_id = settings.CART_SESSION_ID
        self.cart = self._get_or_create_cart()
    def _get_or_create_cart(self):
        """
        Get existing cart or create a new one in session.
        Uses caching for better performance and faster cart retrieval for high concurrent requests.
        """
        if self.request.user.is_authenticated:
        # Use cache to store cart for authenticated users
            cache_key = f"cart_{self.session.session_key}"
            cart = cache.get(cache_key)
        else:
            # For unauthenticated users, use session directly
            cache_key = None
            cart = None
            
        if cart is None:
            cart = self.session.get(self.session_id, {})
            if not isinstance(cart, dict):
                cart = {}
            if self.request.user.is_authenticated:
                cache.set(cache_key, cart, timeout=3600)  #Cache for 1hour
        return cart
    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:

        if quantity <= 0:
            self.remove(product)
            return

        product_slug = str(product.slug)
        product_price = str(product.price)
        product_discount = str(product.discount)
        print(product_discount)
        product_price_after_discount = str(product.price_after_discount)
        
        if product_slug not in self.cart:
            self.cart[product_slug] = {
                'quantity': 0,
                'price': product_price,
                'discount': product_discount,
                'price_after_discount': product_price_after_discount,
                'added_at': timezone.now().isoformat(),
                'total_price': 0
            }

        if override_quantity:
            self.cart[product_slug]['quantity'] = quantity
        else:
            self.cart[product_slug]['quantity'] += quantity

        self.cart[product_slug]['total_price'] = float(product_price_after_discount) * quantity
        
        self.save()
    def remove(self, product: Product) -> None:
        product_slug = str(product.slug)
        if product_slug in self.cart:
            del self.cart[product_slug]
            self.save()
    def clear(self) -> None:

        self.cart = {}
        del self.session[self.session_id]
        self.save(clear=True)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over the items in the cart and fetch the corresponding products.
        Uses iterator() for memory efficiency with large datasets.
        """
        product_slugs = list(self.cart.keys())
        products_query = Product.objects.filter(slug__in=product_slugs).select_related('category').only(
            'slug', 'name', 'price', 'discount', 'image', 'category__name'
        ).iterator()
        
        products_map = {str(p.slug): p for p in products_query}
        
        for slug, item in self.cart.items():
            product = products_map.get(slug)
            if product is None:
                continue
                
            yield {
                'product': product,
                'quantity': item['quantity'],
                'price': Decimal(item['price']),
                'discount': Decimal(item['price']) - Decimal(item['price']) * (100 - Decimal(item['discount'])) / 100,
                'price_after_discount': Decimal(item['price_after_discount']),
                'added_at': item.get('added_at'),
                'total_price': Decimal(item['total_price']),
                
            }

    def __len__(self) -> int:return sum(item['quantity'] for item in self.cart.values())

    def save(self,clear: bool = False) -> None:
        """
        Save the cart state to session and update cache.
        """
        self.session[self.session_id] = self.cart
        self.session.modified = True
        if self.request.user.is_authenticated:
                self._update_cache(clear=clear)        
    def _update_cache(self, clear: bool = False) -> None:
        cache_key = f"cart_{self.session.session_key}"
        if clear:
            cache.delete(cache_key)
        else:
            cache.set(cache_key, self.cart, timeout=3600)
    def get_total_price(self):return sum(Decimal(item['price']) * item['quantity']for item in self.cart.values())
    def get_total_discount(self):return sum((Decimal(item['price']) * item['quantity']) * (Decimal(item['discount']) / 100) for item in self.cart.values()) 
    def get_total_price_after_discount(self):return (self.get_total_price() - self.get_total_discount())
    def get_cart_summary(self) -> Dict[str, Any]:

        return {
            'total_items': len(self),
            'total_price': self.get_total_price(),
            'total_discount': self.get_total_discount(),
            'total_price_after_discount': self.get_total_price_after_discount()
        }


