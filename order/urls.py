
from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
)
app_name = 'order'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='detail'),
]
