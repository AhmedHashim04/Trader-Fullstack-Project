import pytest
from django.urls import reverse, resolve
from cart.views import CartView, cart_add, cart_remove, cart_update, cart_clear

@pytest.mark.parametrize("url_name, view_class, url_kwargs", [
    ('cart:cart_list', CartView, {}),
    ('cart:cart_add', cart_add, {'slug': '1'}),
    ('cart:cart_remove', cart_remove, {'slug': '1'}),
    ('cart:cart_update', cart_update, {'slug': '1'}),
    ('cart:cart_clear', cart_clear, {'slug': '1'}),


])
def test_url_resolves_to_correct_view(url_name, view_class, url_kwargs):
    url = reverse(url_name, kwargs=url_kwargs)
    assert resolve(url).func.view_class == view_class

