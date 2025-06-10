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
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from features.models import Brand
from django.core.cache import cache
from django.http import Http404
from django.db.models import Q, Avg, Count
from django.utils.functional import cached_property
from django.utils.http import urlencode

class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product/products.html'
    paginate_by = 12  # default

    @cached_property
    def filters(self):
        """Extract and validate filters from request GET parameters"""
        params = self.request.GET.copy()
        filters = {
            'search_query': params.get('search', '').strip(),
            'category_slug': params.get('category', '').strip(),
            'brand_slug': params.get('brand', '').strip(),
            'sort_by': params.get('sort_by', '').strip(),
            'min_price': params.get('min_price', '').strip(),
            'max_price': params.get('max_price', '').strip(),
            'view_mode': params.get('view_mode', 'grid'),
            'items_per_page': params.get('items_per_page', self.paginate_by),
        }
        
        # Validate items_per_page
        try:
            filters['items_per_page'] = int(filters['items_per_page'])
            if filters['items_per_page'] not in [12, 24, 48]:
                filters['items_per_page'] = self.paginate_by
        except (ValueError, TypeError):
            filters['items_per_page'] = self.paginate_by
            
        return filters

    def get_queryset(self):
        """Get and filter products with caching"""
        cache_key = f"products_{urlencode(self.request.GET)}"
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = super().get_queryset()
            
            # Annotate with average rating and review count
            queryset = queryset.annotate(
                average_rating=Avg('product_review__rating'),  # استبدل reviews بـ product_review
                review_count=Count('product_review')          # استبدل reviews بـ product_review
            )
            
            # Apply filters
            filters = self.filters
            
            if filters['search_query']:
                queryset = queryset.filter(
                    Q(name__icontains=filters['search_query']) |
                    Q(description__icontains=filters['search_query']) |
                    Q(category__name__icontains=filters['search_query']) |
                    Q(brand__name__icontains=filters['search_query'])
                )
            
            if filters['category_slug']:
                queryset = queryset.filter(category__slug=filters['category_slug'])
            
            if filters['brand_slug']:
                queryset = queryset.filter(brand__slug=filters['brand_slug'])
            
            if filters['min_price']:
                try:
                    queryset = queryset.filter(price__gte=float(filters['min_price']))
                except (ValueError, TypeError):
                    pass
            
            if filters['max_price']:
                try:
                    queryset = queryset.filter(price__lte=float(filters['max_price']))
                except (ValueError, TypeError):
                    pass
            
            # Apply sorting
            sorting_map = {
                'price_asc': 'price',
                'price_desc': '-price',
                'name_asc': 'name',
                'name_desc': '-name',
                'rating_desc': '-average_rating',
                'popularity': '-review_count',
            }
            
            if filters['sort_by'] in sorting_map:
                queryset = queryset.order_by(sorting_map[filters['sort_by']])
            
            # Cache the queryset for 5 minutes
            cache.set(cache_key, queryset, 300)
        
        return queryset

    def get_paginate_by(self, queryset):
        """Get number of items per page"""
        return self.filters['items_per_page']

    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        filters = self.filters
        
        context.update({
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'search_query': filters['search_query'],
            'selected_category': filters['category_slug'],
            'selected_brand': filters['brand_slug'],
            'sort_by': filters['sort_by'],
            'min_price': filters['min_price'],
            'max_price': filters['max_price'],
            'items_per_page': filters['items_per_page'],
            'view_mode': filters['view_mode'],
            'is_paginated': context['page_obj'].has_other_pages(),
        })
        
        return context

# Helper template tag for querystring manipulation
from django import template

register = template.Library

@register.simple_tag
def querystring(request, **kwargs):
    """
    Creates a URL with the current request's querystring, updated with the given parameters.
    Usage: {% querystring request page=1 category='electronics' %}
    """
    query = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == '':
            if key in query:
                del query[key]
        else:
            query[key] = value
    return query.urlencode()


class CompareProductsView(LoginRequiredMixin, TemplateView):
    template_name = 'product/compare_products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_slugs = self.request.GET.getlist('product_slug')[:4]  # Limit to 4 products
        
        if not product_slugs or len(product_slugs) < 2:
            raise Http404("You need to select at least 2 products to compare")
        
        products = Product.objects.filter(slug__in=product_slugs)
        
        # Get comparable fields (exclude non-comparable fields)
        excluded_fields = ['id', 'slug', 'image', 'created_at', 'updated_at', 'user', 'description']
        fields = [
            field for field in Product._meta.get_fields() 
            if not field.many_to_many and 
                not field.one_to_many and 
                field.name not in excluded_fields
        ]
        
        # Prepare specifications data
        specifications = []
        for field in fields:
            field_name = field.name.replace('_', ' ').title()
            values = [getattr(product, field.name) for product in products]
            
            # Skip fields where all values are empty
            if all(v is None or v == '' for v in values):
                continue
                
            specifications.append({
                'name': field_name,
                'values': values
            })
        
        context.update({
            'products': products,
            'specifications': specifications,
            'product_count': len(products),
        })
        
        return context


from django.views.generic.edit import FormMixin
class ProductViewDetail(LoginRequiredMixin, FormMixin, DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = "slug"
    slug_url_kwarg = "slug"
    form_class = ReviewForm

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Update recently viewed products
        recently_viewed = self.update_recently_viewed(product)
        
        # Get reviews with rating filter
        reviews_qs = Review.objects.filter(product=product).select_related('user')
        rating_filter = self.request.GET.get('rating')
        if rating_filter and rating_filter.isdigit():
            reviews_qs = reviews_qs.filter(rating=int(rating_filter))
        
        # Pagination
        paginator = Paginator(reviews_qs, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Related products (same category, exclude current product)
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).order_by('?')[:4]
        
        context.update({
            'review_form': kwargs.get('form', ReviewForm()),
            'reviews': reviews_qs,
            'reviews_count': reviews_qs.count(),
            'overall_rating': product.calculate_overall_rating(reviews_qs),
            'related_products': related_products,
            'recently_viewed': recently_viewed,
            'page_obj': page_obj,
        })
        return context

    def update_recently_viewed(self, product):
        """Update session with recently viewed products"""
        recently_viewed = self.request.session.get('recently_viewed', [])
        
        if product.id in recently_viewed:
            recently_viewed.remove(product.id)
        
        recently_viewed.insert(0, product.id)
        
        # Keep only last 6 viewed products
        if len(recently_viewed) > 6:
            recently_viewed = recently_viewed[:6]
        
        self.request.session['recently_viewed'] = recently_viewed
        
        # Return actual product objects
        return Product.objects.filter(id__in=recently_viewed).exclude(id=product.id)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.user = self.request.user
        review.product = self.object
        review.save()
        
        # Update product rating
        self.object.update_overall_rating()
        
        messages.success(self.request, 'Thank you for your review!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class WishlistViewDetail(LoginRequiredMixin, TemplateView):
    template_name = 'product/wishlist.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_profile = get_object_or_404(Profile, user=self.request.user)
        wishlist_products = user_profile.wishlist.select_related('category', 'brand')

        context.update({
            'wishlist_products': wishlist_products,
            'wishlist_count': wishlist_products.count(),
        })
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



@login_required
def clear_wishlist(request):
    user = get_object_or_404(Profile, user=request.user)
    print("Adsd")
    user.wishlist.clear()
    messages.success(request, 'Wishlist cleared successfully!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))





def user_see_product(request,slug):
    product = Product.objects.get(slug=slug)
    user = get_object_or_404(Profile, user=request.user)
    if user not in product.viewed_by.all() :
        product.viewed_by.add(user)

    return redirect(product.get_absolute_url())  

