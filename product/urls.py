from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    WishlistViewDetail,
    clear_wishlist,
    user_see_product,
    add_remove_wishlist,
    CompareProductsView,
)

app_name = 'product'


urlpatterns = [
    path('', ProductListView.as_view(), name="products_list"),
    path('wishlist/', WishlistViewDetail.as_view(), name="wishlist"),
    path('compare/', CompareProductsView.as_view(), name='compare_products'),
    path('clear-wishlist/', clear_wishlist, name="clear_wishlist"),
    path('<slug:slug>/', ProductDetailView.as_view(), name="product_detail"),
    path('<slug:slug>/view/', user_see_product, name="product_view"),
    path('<slug:slug>/wishlist/', add_remove_wishlist, name="add_remove_wishlist"),

]
