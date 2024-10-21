from typing import Any
from django.db.models.base import Model as Model
from django.shortcuts import redirect ,get_object_or_404 
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView ,DetailView, TemplateView
from .models import *
from accounts.models import Profile
from .form import ReviewForm
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.db import transaction

class ProductsView(ListView):
    model = Product
    context_object_name = 'all_products'
    template_name = 'product/products.html'
    # paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        sort_by = self.request.GET.get('sort_by', '')

        if search_query:
            queryset = queryset.filter(
                Q(PRDname__icontains=search_query) | 
                Q(PRDdesc__icontains=search_query)
            )
        
        if category:
            queryset = queryset.filter(PRDcategory__CATslug=category)
        
        order_by_mapping = {
            'price_asc': 'PRDprice',
            'price_desc': '-PRDprice',
            'rating': '-overall_rating'
        }
        if sort_by in order_by_mapping:
            queryset = queryset.order_by(order_by_mapping[sort_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'search_query': self.request.GET.get('search', ''),
            'selected_category': self.request.GET.get('category', ''),
            'sort_by': self.request.GET.get('sort_by', '')
        })
        return context

class CompareProductsView(TemplateView):
    template_name = 'product/compare_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_ids = self.request.GET.getlist('product_id')
        products = Product.objects.filter(id__in=product_ids)
        context['products'] = products
        
        for product in products:
            product.overall_rating = self.calculate_product_rating(product)
        
        return context
    
    def calculate_product_rating(self, product):
        reviews = Review.objects.filter(REVproduct=product)
        if reviews.exists():
            total_rating = sum(review.REVrating for review in reviews)
            num_reviews = reviews.count()
            return round(total_rating / num_reviews, 1)
        return 0

class ProductViewDetail(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = "PRDslug"
    slug_url_kwarg = "slug"


    def calculate_overall_rating(self, reviews):
        if not reviews.exists():
            return 0 

        total_rating = sum([review.REVrating for review in reviews])

        num_reviews = reviews.count()

        return round(total_rating / num_reviews, 1)


    def get_context_data(self, **kwargs):
        user_profile = Profile.objects.get(PRFuser=self.request.user)

        love_products = user_profile.PRFlove.all()

        context = super().get_context_data(**kwargs)
        context['form']             = ReviewForm()
        context['reviews']          = Review.objects.filter(REVproduct=self.get_object())
        context['overall_rating']   = self.calculate_overall_rating(context['reviews'])

        context['in_love'] = self.get_object() in love_products

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.REVuser = request.user
            review.REVproduct = product
            review.save()
            product.update_overall_rating()
            messages.success(self.request, 'Review and rating submitted successfully!')
            return redirect(product.get_absolute_url())

        return self.render_to_response(self.get_context_data(form=form))
 
class CategorysView(ListView):
    model = Category
    context_object_name = 'all_categories'
    template_name='product/categories.html'
    paginate_by = 12

class CategoryViewDetail(DetailView):
    model = Category
    template_name = 'product/category_detail.html'
    context_object_name = 'category'
    slug_field     = "CATslug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        obj = self.get_object()
        context['categoryProducts'] = Product.objects.filter(PRDcategory=obj)  
        
        return context

class LoveViewDetail(DetailView):
    model = Profile
    template_name = 'product/love.html'
    context_object_name = 'profile'
    slug_field     = "PRFslug"
    slug_url_kwarg = "slug"
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context
    



@login_required
def add_remove_love(request,slug):
    product = Product.objects.get(PRDslug=slug)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if product in user.PRFlove.all() :
        user.PRFlove.remove(product)
        messages.success(request, 'The product has been removed from the wishlist!')
    else:
        user.PRFlove.add(product)
        messages.success(request, 'Product added to Wishlist successfully!')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def user_see_product(request,slug):
    product = Product.objects.get(PRDslug=slug)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if user not in product.PRDview.all() :
        product.PRDview.add(user)

    return redirect(product.get_absolute_url())  

