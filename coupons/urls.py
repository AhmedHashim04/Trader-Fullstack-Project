from django.urls import path
from .views import  apply_coupon

app_name = 'coupons'

urlpatterns = [
    
path('apply/', apply_coupon, name='coupon_apply'),
]
