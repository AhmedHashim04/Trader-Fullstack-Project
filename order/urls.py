from django.urls import path
from .views import create_order, OrderListView, OrderDetailView, CheckoutView, clear_order_history , confirm_order

app_name = 'order'

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<str:id>/', OrderDetailView.as_view(), name='order_detail'),
    path('checkout/<str:id>/', CheckoutView.as_view(), name='checkout'),
    path('create-order/', create_order, name='create_order'),
    path('clear-order-history/', clear_order_history, name='clear_order_history'),
    path('confirm/<str:confirmation_key>/', confirm_order, name='confirm_order'),

]
