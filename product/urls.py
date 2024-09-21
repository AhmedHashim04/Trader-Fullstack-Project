from django.urls import path , include
from .views import *

app_name = 'product'

urlpatterns = [
    path('products/',ProductsView.as_view() , name="products_list"),
    path('product/<int:pk>',ProductViewDetail.as_view() , name="product_detail"),
    path('products/<int:product_id>/view',user_see_product, name="view"),
    path('products/<int:product_id>/love',add_remove_love , name="love"),
    path('products/<int:product_id>/cart',add_remove_cart , name="cart"),
]
