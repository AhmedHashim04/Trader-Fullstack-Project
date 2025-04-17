from django.shortcuts import render
from django.views.generic import ListView ,DetailView
from .models import Brand
from product.models import Product 
# Create your views here.

class BrandListView(ListView):
    model = Brand
    template_name = 'settings/brands.html'
    context_object_name = 'brands'
    
class BrandViewDetail(DetailView):
    model = Brand
    template_name = 'settings/brand_detail.html'
    context_object_name = 'brand'
    slug_field     = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs) 
        obj = self.get_object()
        context['brandProducts'] = Product.objects.filter(brand=obj)  
        
        return context