from django.urls import path
from .views import (
    ProductsView,
    ProductViewDetail,
    CategorysView,
    CategoryViewDetail,
    WishlistViewDetail,
    user_see_product,
    add_remove_wishlist,
    CompareProductsView,
)

app_name = 'product'


urlpatterns = [
    path('', ProductsView.as_view(), name="products_list"),
    path('categories/', CategorysView.as_view(), name="categories_list"),
    path('category/<slug:slug>/', CategoryViewDetail.as_view(), name="category_detail"),
    path('wishlist/<slug:id>/', WishlistViewDetail.as_view(), name="wishlist_detail"),
    path('compare/', CompareProductsView.as_view(), name='compare_products'),
    path('<slug:slug>/', ProductViewDetail.as_view(), name="product_detail"),
    path('<slug:slug>/view/', user_see_product, name="product_view"),
    path('<slug:slug>/wishlist/', add_remove_wishlist, name="product_wishlist"),
]
