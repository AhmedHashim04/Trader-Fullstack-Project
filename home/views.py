from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import *
from settings.models import Brand
from django.utils import timezone


class HomeView(TemplateView):
    template_name = "home/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['featuredProducts'] = Product.objects.filter(created_at__lt=timezone.now()).order_by('-created_at')[:4]
        context['featuredCategories'] = Category.objects.filter(parent=None) 
        context['featuredBrands'] = Brand.objects.all() 
        context['random_products'] = Product.objects.all().order_by('?')[:3]

        for product in context['featuredProducts']:
            reviews = Review.objects.filter(product=product)  
            product.overall_rating = Product.calculate_overall_rating(reviews)  

        return context

