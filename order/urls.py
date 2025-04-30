from django.urls import path
from .views import (
    create_order,
    confirm_order,
    OrderListView,
    OrderDetailView,
    CheckoutView,
    PreviewView,
    clear_order_history,
)

app_name = 'order'

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order_list'), 
    path('order/<str:id>/', OrderDetailView.as_view(), name='order_detail'),  
    path('checkout/<str:id>/', CheckoutView.as_view(), name='checkout'),
    path('preview/', PreviewView.as_view(), name='preview_order'), 
    path('create-order/', create_order, name='create_order'), 
    path('confirm/<str:confirmation_key>/', confirm_order, name='confirm_order'),  
    path('clear-order-history/', clear_order_history, name='clear_order_history'),  
]