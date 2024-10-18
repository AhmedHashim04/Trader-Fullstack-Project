from django.urls import path , include
from .views import *

app_name = 'product'

urlpatterns = [
     
    path('products/',ProductsView.as_view() , name="products_list"),
    path('product/<slug:slug>',ProductViewDetail.as_view() , name="product_detail"),
    path('categories/',CategorysView.as_view() , name="categories_list"),
    path('category/<slug:slug>',CategoryViewDetail.as_view() , name="category_detail"),
    path('love/<slug:slug>',LoveViewDetail.as_view() , name="love_detail"),
    path('products/<slug:slug>/view',user_see_product, name="view"),
    path('products/<slug:slug>/love',add_remove_love , name="love"),
    path('compare/', CompareProductsView.as_view(), name='compare_products'),

] 
