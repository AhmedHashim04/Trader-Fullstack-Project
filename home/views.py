from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import *
from features.models import Brand, Collection


class HomeView(TemplateView):
    template_name = "home/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['featuredProducts'] = Product.objects.filter(trending=True).order_by('-created_at')[:6]
        context['featuredCategories'] = Category.objects.filter(parent=None) 
        context['featuredBrands'] = Brand.objects.all() 
        context['featuredCollections'] = Collection.objects.all()

        for product in context['featuredProducts']:
            reviews = Review.objects.filter(product=product)  

        return context

class AboutView(TemplateView):
    template_name = "home/about.html"