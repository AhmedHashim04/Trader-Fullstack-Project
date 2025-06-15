from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import *
from features.models import Brand, Collection


class HomeView(TemplateView):
    template_name = "home/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_filter = self.request.GET.get('tag')
        if tag_filter and tag_filter != 'all':
            context['featuredProducts'] = Product.objects.filter(trending=True, tags__name__iexact=tag_filter).order_by('-created_at')[:6]
        else:
            context['featuredProducts'] = Product.objects.filter(trending=True).order_by('-created_at')[:6]
        context['tags'] = Tag.objects.all()
        context['featuredCategories'] = Category.objects.filter(parent=None)
        context['featuredBrands'] = Brand.objects.all()
        context['featuredCollections'] = Collection.objects.all()
        context['active_tag'] = tag_filter or 'all'
        return context

class AboutView(TemplateView):
    template_name = "home/about.html"