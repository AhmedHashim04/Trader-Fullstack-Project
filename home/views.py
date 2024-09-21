from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import *
from django.utils import timezone

# Create your views here.


class HomeView(TemplateView):
    template_name = "home/index.html"
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['all_products'] = Product.objects.filter(PRDcreated__lt=timezone.now()).order_by('-PRDcreated')[:5]
        context['categories'] = Category.objects.filter(CATparent=None) 
        context['alternatives'] = Alternative.objects.all()  
        return context

    

