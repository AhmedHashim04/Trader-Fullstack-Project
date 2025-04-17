from typing import Any
from django.db.models.base import Model as Model
from django.shortcuts import redirect ,get_object_or_404 
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView ,DetailView, TemplateView ,CreateView
from .models import Product ,Category , Review
from account.models import Profile
from .form import ReviewForm
from django.contrib.auth.decorators import login_required

from django.db.models import Q

class ProductsView(ListView):
    model = Product
    context_object_name = 'all_products'
    template_name = 'product/products.html'
    paginate_by = 12
    

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        sort_by = self.request.GET.get('sort_by', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(desc__icontains=search_query)
            )

        if category:
            queryset = queryset.filter(category__slug=category)
        
        order_by_mapping = {
            'price_asc': 'price',
            'price_desc': '-price',
            'rating': '-overall_rating'
        }
        if sort_by in order_by_mapping:
            queryset = queryset.order_by(order_by_mapping[sort_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context.update({
            'categories': Category.objects.all(),
            'search_query': self.request.GET.get('search', ''),
            'selected_category': self.request.GET.get('category', ''),
            'sort_by': self.request.GET.get('sort_by', ''),
            'all_products': page_obj,
            'is_paginated': page_obj.has_other_pages()
        })

        return context
class CompareProductsView(LoginRequiredMixin , TemplateView):
    template_name = 'product/compare_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product_ids = self.request.GET.getlist('product_id')
        products = Product.objects.filter(id__in=product_ids)
        context['products'] = products
        return context


class ProductViewDetail(LoginRequiredMixin, DetailView ,CreateView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = "slug"
    slug_url_kwarg = "slug"
    form_class = ReviewForm


    def get_context_data(self, **kwargs):
        product = self.get_object()  
        context = super().get_context_data(**kwargs)
        reviews = Review.objects.filter(product=product)

        context['review_form'] = ReviewForm()
        context['reviews'] = reviews
        context['overall_rating'] = product.calculate_overall_rating(reviews)
        return context
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = self.object
            review.save()
            self.object.update_overall_rating()
            messages.success(self.request, 'Review and rating submitted successfully!')
            return redirect(self.object.get_absolute_url())
        
        messages.error(self.request, 'Review and rating not submitted successfully!')
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
    slug_field     = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        obj = self.get_object()
        
        # Get the products that belong to the category and add pagination
        category_products = Product.objects.filter(category=obj)
        paginator = Paginator(category_products, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'all_products': page_obj,
            'is_paginated': page_obj.has_other_pages()
        })
                    
        return context

class WishlistViewDetail(DetailView):
    model = Profile
    template_name = 'product/wishlist.html'
    context_object_name = 'profile'
    slug_field     = "id"
    slug_url_kwarg = "id"
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context

@login_required
def add_remove_wishlist(request,slug):
    product = Product.objects.get(slug=slug)

    user = get_object_or_404(Profile, user=request.user)
    
    if product in user.wishlist.all() :
        user.wishlist.remove(product)
        messages.success(request, 'The product has been removed from the wishlist!')
    else:
        user.wishlist.add(product)
        messages.success(request, 'Product added to Wishlist successfully!')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def user_see_product(request,slug):
    product = Product.objects.get(slug=slug)
    user = get_object_or_404(Profile, user=request.user)
    if user not in product.viewed_by.all() :
        product.viewed_by.add(user)

    return redirect(product.get_absolute_url())  

