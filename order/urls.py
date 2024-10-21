from django.urls import path
from .views import create_order, OrderListView, OrderDetailView, clear_order_history

app_name = 'order'

urlpatterns = [
    path('create-order/', create_order, name='create_order'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<slug:slug>/', OrderDetailView.as_view(), name='order_detail'),
    path('clear-order-history/', clear_order_history, name='clear_order_history'),
]
