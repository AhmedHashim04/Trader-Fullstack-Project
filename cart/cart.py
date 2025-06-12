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
        self.session = request.session
        self.session_id = settings.CART_SESSION_ID
        self.cart = self._get_or_create_cart()

    def _get_or_create_cart(self):
        """
        Get existing cart or create a new one in session.
        Uses caching for better performance.
        """
        cache_key = f"cart_{self.session.session_key}"
        cart = cache.get(cache_key)

        if cart is None:
            cart = self.session.get(self.session_id, {})
            if not isinstance(cart, dict):
                cart = {}
            cache.set(cache_key, cart, timeout=3600)  # Cache for 1 hour
        return cart

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add a product to the cart or update its quantity.
        """
        if quantity <= 0:
            self.remove(product)
            return

        product_slug = str(product.slug)
        product_price = str(product.price)
        product_discount = str(product.discount)
        
        if product_slug not in self.cart:
            self.cart[product_slug] = {
                'quantity': 0,
                'price': product_price,
                'discount': product_discount,
                'added_at': timezone.now().isoformat()
            }
        
        if override_quantity:
            self.cart[product_slug]['quantity'] = quantity
        else:
            self.cart[product_slug]['quantity'] += quantity
            
        self._update_cache()
        self.save()

    def remove(self, product: Product) -> None:
        """
        Remove a product from the cart.
        """
        product_slug = str(product.slug)
        if product_slug in self.cart:
            del self.cart[product_slug]
            self._update_cache()
            self.save()

    def get_total_price(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_total_discount(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.
        """
        return sum(
            Decimal(item['discount']) * item['quantity']
            for item in self.cart.values()
        )

    def get_total_price_after_discount(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.
        """
        return sum(
            (Decimal(item['price']) - Decimal(item['discount'])) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self) -> None:
        """
        Remove all items from the cart.
        """
        self.cart = {}
        self.session[self.session_id] = {}
        self._update_cache(clear=True)
        self.save()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over the items in the cart and fetch the corresponding products.
        Uses bulk query for better performance.
        """
        product_slugs = list(self.cart.keys())
        products_map = {
            str(p.slug): p 
            for p in Product.objects.filter(
                slug__in=product_slugs
            ).select_related('category').only(
                'slug', 'name', 'price', 'discount', 'image', 'category__name'
            )
        }
        
        for slug, item in self.cart.items():
            product = products_map.get(slug)
            if product is None:
                continue
                
            yield {
                'product': product,
                'quantity': item['quantity'],
                'price': Decimal(item['price']),
                'discount': Decimal(item['discount']),
                'added_at': item.get('added_at'),
                'price_after_discount': (Decimal(item['price']) - Decimal(item['discount'])),
                'total_price_after_discount': (Decimal(item['price']) - Decimal(item['discount'])) * item['quantity']
            }

    def __len__(self) -> int:
        """
        Return the total number of items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def save(self) -> None:
        """
        Save the cart state to session and update cache.
        """
        self.session[self.session_id] = self.cart
        self.session.modified = True
        self._update_cache()

    def _update_cache(self, clear: bool = False) -> None:
        """
        Update the cached cart data.
        """
        cache_key = f"cart_{self.session.session_key}"
        if clear:
            cache.delete(cache_key)
        else:
            cache.set(cache_key, self.cart, timeout=3600)


    def get_cart_summary(self) -> Dict[str, Any]:
        """
        Return a summary of the cart contents with totals.
        """
        return {
            'total_items': len(self),
            'total_price': self.get_total_price(),
            'total_price_after_discount': self.get_total_price_after_discount()
        }