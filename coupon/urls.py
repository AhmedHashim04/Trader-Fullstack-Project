from django.urls import path
from . import views

app_name = 'coupon'

urlpatterns = [
    path('', views.coupon_list, name='coupon_list'),
    path('apply/', views.apply_coupon, name='apply_coupon'),
    path('remove/', views.remove_coupon, name='remove_coupon'),
    path('my-coupons/', views.my_coupons, name='my_coupons'),
]