from django.shortcuts import render
from django.views.generic import ListView
from .models import Brand, Collection
from product.models import Product, Category
# Create your views here.
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q

class CollectionDetailView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'features/collection_detail.html'  # تقدر تخصص Template لو حبيت
    paginate_by = 12

    def get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset

        slug = self.kwargs.get('slug')
        collection = Collection.objects.filter(slug=slug).first()
        if not collection:
            return Product.objects.none()

        query_params = self.request.GET.copy()
        cache_key = f"collection_{slug}_{query_params.urlencode()}"
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = collection.products.filter()

            # Apply filters
            search_query = query_params.get('search', '').strip()
            category_slug = query_params.get('category', '').strip()
            brand_slug = query_params.get('brand', '').strip()
            sort_by = query_params.get('sort_by', '').strip()
            min_price = query_params.get('min_price', '').strip()
            max_price = query_params.get('max_price', '').strip()

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
            cache.set(cache_key, queryset, timeout=300)

        self._queryset = queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by(queryset)
        paginator = Paginator(queryset, paginate_by)
        page_number = self.request.GET.get("page")
        products = paginator.get_page(page_number)

        slug = self.kwargs.get('slug')
        collection = Collection.objects.filter(slug=slug).first()

        context.update({
            'collection': collection,
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
    


