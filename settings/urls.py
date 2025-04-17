from django.urls import path
from .views import BrandListView ,BrandViewDetail

app_name = 'settings'


urlpatterns = [

    path('', BrandListView.as_view(), name="brands_list"),
    path('<slug:slug>/', BrandViewDetail.as_view(), name="brand_detail"),
]
