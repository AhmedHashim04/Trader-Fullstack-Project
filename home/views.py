from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import *
from django.utils import timezone
import random
# Create your views here.


class HomeView(TemplateView):
    template_name = "home/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['all_products'] = Product.objects.filter(PRDcreated__lt=timezone.now()).order_by('-PRDcreated')[:3]
        context['random_products'] = random.sample(list(context['all_products']), min(len(context['all_products']), 3))
        
        context['all_categories'] = Category.objects.filter(CATparent=None) 
        context['alternatives'] = Alternative.objects.all()
        for product in context['all_products']:
            reviews = Review.objects.filter(REVproduct=product)  # استرجاع التقييمات الخاصة بالمنتج
            product.overall_rating = Product.calculate_overall_rating(reviews)  # حساب التقييم الكلي

        return context
        return context

