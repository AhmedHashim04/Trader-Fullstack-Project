
from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderCancelView,
    address_list_create_view
)
app_name = 'order'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='create_order'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<uuid:pk>/cancel/', OrderCancelView.as_view(), name='cancel_order'),
    path('addresses/', address_list_create_view, name='address'),
]
