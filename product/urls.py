from django.urls import path , include
from .views import *

app_name = 'product'

urlpatterns = [
    path('products/',ProductsView.as_view() , name="products_list"),
    path('product/<int:pk>',ProductViewDetail.as_view() , name="product_detail"),
    path('category/<int:pk>',CategoryViewDetail.as_view() , name="category_detail"),
    path('cart/<int:pk>',CartViewDetail.as_view() , name="cart_detail"),
    path('love/<int:pk>',LoveViewDetail.as_view() , name="love_detail"),
    path('products/<int:product_id>/view',user_see_product, name="view"),
    path('products/<int:product_id>/love',add_remove_love , name="love"),
    path('products/<int:product_id>/cart',add_remove_cart , name="cart"),
]
