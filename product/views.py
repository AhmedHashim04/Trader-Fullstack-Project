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
from django.db.models import Q

class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product/products.html'
    paginate_by = 12  # default

    def get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset

        query_params = self.request.GET.copy()
        cache_key = f"products_{query_params.urlencode()}"
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = super().get_queryset()

            # Get filters
            search_query = query_params.get('search', '').strip()
            category_slug = query_params.get('category', '').strip()
            brand_slug = query_params.get('brand', '').strip()
            sort_by = query_params.get('sort_by', '').strip()
            min_price = query_params.get('min_price', '').strip()
            max_price = query_params.get('max_price', '').strip()

            # Apply filters
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query)
                )

            if category_slug and category_slug.lower() != "none":
                queryset = queryset.filter(category__slug=category_slug)

            if brand_slug and brand_slug.lower() != "none":
                queryset = queryset.filter(brand__slug=brand_slug)

            if min_price:
                try:
                    queryset = queryset.filter(price__gte=float(min_price))
                except ValueError:
                    pass

            if max_price:
                try:
                    queryset = queryset.filter(price__lte=float(max_price))
                except ValueError:
                    pass

            if sort_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort_by == 'name_asc':
                queryset = queryset.order_by('name')
            elif sort_by == 'name_desc':
                queryset = queryset.order_by('-name')

            queryset = list(queryset)
            cache.set(cache_key, queryset, timeout=300)  # Cache for 5 mins

        self._queryset = queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        paginate_by = self.get_paginate_by(queryset)
        paginator = Paginator(queryset, paginate_by)
        page_number = self.request.GET.get("page")
        products = paginator.get_page(page_number)

        context.update({
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'search_query': self.request.GET.get('search', ''),
            'selected_category': self.request.GET.get('category', ''),
            'selected_brand': self.request.GET.get('brand', ''),
            'sort_by': self.request.GET.get('sort_by', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'items_per_page': self.request.GET.get('items_per_page', paginate_by),
            'view_mode': self.request.GET.get('view_mode', 'grid'),
            'products': products,
            'is_paginated': products.has_other_pages(),
        })
        return context


class CompareProductsView(LoginRequiredMixin, TemplateView):
    template_name = 'product/compare_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product_slugs = self.request.GET.getlist('product_slug')
        products = Product.objects.filter(slug__in=product_slugs)
        fields = [field for field in Product._meta.get_fields() if not field.many_to_many and not field.one_to_many]

        context['products'] = products
        context['fields'] = fields
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
        reviews_qs = Review.objects.filter(product=product).select_related('user')
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    # Filter by rating if specified
        rating_filter = self.request.GET.get('rating')
        if rating_filter and rating_filter.isdigit():
            reviews_qs = reviews_qs.filter(rating=int(rating_filter))

        paginator = Paginator(reviews_qs, 4)  # 4 reviews per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

 
        context.update({
            'review_form': kwargs.get('form', ReviewForm()),
            'reviews': reviews_qs,
            'reviews_count': reviews_qs.count(),
            'overall_rating': product.calculate_overall_rating(reviews_qs),
            'related_products': Product.objects.filter(category=product.category).exclude(id=product.id)[:4],
            'page_obj': page_obj,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # required for get_success_url()
        form = self.get_form()

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = self.object
            review.save()
            self.object.update_overall_rating()
            messages.success(request, 'Your review was submitted successfully.')
            return redirect(self.get_success_url())

        messages.error(request, 'Failed to submit your review. Please correct the errors below.')
        return self.form_invalid(form)

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
    user.wishlist.clear()
    messages.success(request, 'Wishlist cleared successfully!')
    return redirect('product:wishlist', id=user.id)

def user_see_product(request,slug):
    product = Product.objects.get(slug=slug)
    user = get_object_or_404(Profile, user=request.user)
    if user not in product.viewed_by.all() :
        product.viewed_by.add(user)

    return redirect(product.get_absolute_url())  

