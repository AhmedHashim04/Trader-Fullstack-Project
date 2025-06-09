from django.urls import path
from . import views
app_name = 'features'


urlpatterns = [

    
    path('collections/<str:slug>/', views.CollectionDetailView.as_view(), name='collection_detail'),

]
