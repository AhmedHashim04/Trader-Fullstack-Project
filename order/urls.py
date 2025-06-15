
from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    address_list_create_view
)
app_name = 'order'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='create_order'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('addresses/', address_list_create_view, name='address'),
]
