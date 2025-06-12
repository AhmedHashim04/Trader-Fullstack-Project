
from django.urls import path
from .views import CartView, cart_add, cart_remove, cart_clear


app_name = 'cart'
urlpatterns = [
    path('', CartView.as_view(), name='cart_list'),
    path('add/<slug:slug>/', cart_add, name='cart_add'),
    path('remove/<slug:slug>/', cart_remove, name='cart_remove'),
    path('clear/', cart_clear, name='cart_clear'),

]

