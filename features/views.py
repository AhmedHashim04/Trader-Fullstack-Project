from django.utils.http import urlencode
from .models import Brand, Collection
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q
from django.utils.functional import cached_property
from product.models import Product, Category, Tag
from features.models import Brand
from django.db import models
import decimal

class CollectionDetailView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'features/collection_detail.html'
    paginate_by = 12
    sort_options = {
        'default': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'rating_desc': '-overall_rating',
        'popularity': '-review_count',
    }
    items_per_page_options = [12, 24, 48]

    @cached_property
    def applied_filters(self):
        """Extract and sanitize filter parameters"""
        params = self.request.GET.copy()
        return {
            'search': params.get('search', '').strip(),
            'tag': params.get('tag', '').strip(),
            'category': params.get('category', '').strip(),
            'brand': params.get('brand', '').strip(),
            'sort_by': params.get('sort_by', 'default'),
            'min_price': params.get('min_price', ''),
            'max_price': params.get('max_price', ''),
            'view_mode': params.get('view_mode', 'grid'),
            'items_per_page': params.get('items_per_page', str(self.paginate_by)),
        }

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
            filters = self.applied_filters
            
            # Apply search filter
            if filters['search']:
                queryset = queryset.filter(
                    Q(name__icontains=filters['search']) |
                    Q(description__icontains=filters['search']) |
                    Q(category__name__icontains=filters['search']) |
                    Q(brand__name__icontains=filters['search'])
                )
            
            # Apply category filter
            if filters['category']:
                queryset = queryset.filter(category__slug=filters['category'])
            
            # Apply tag filter  
            if filters['tag']:
                queryset = queryset.filter(tags__name__iexact=filters['tag'])

            # Apply brand filter
            if filters['brand']:
                queryset = queryset.filter(brand__slug=filters['brand'])
            
            # Apply price range filter
            try:
                min_price = float(filters['min_price']) if filters['min_price'] else 0
                queryset = queryset.filter(price__gte=min_price)
            except (ValueError, TypeError):
                pass
            
            try:
                max_price = float(filters['max_price']) if filters['max_price'] else decimal('inf')
                queryset = queryset.filter(price__lte=max_price)
            except (ValueError, TypeError):
                pass
            
            # Apply sorting
            sort_field = self.sort_options.get(
                filters['sort_by'], 
                self.sort_options['default']
            )
            queryset = queryset.order_by(sort_field)
            
            # Cache for 5 minutes
            cache.set(cache_key, queryset, 300)
        
        return queryset

    def get_paginate_by(self, queryset):
        """Get validated items per page setting"""
        try:
            per_page = int(self.applied_filters['items_per_page'])
            return per_page if per_page in self.items_per_page_options else self.paginate_by
        except (ValueError, TypeError):
            return self.paginate_by
    def get_context_data(self, **kwargs):
        """Add filtering context and aggregations"""
        context = super().get_context_data(**kwargs)
        filters = self.applied_filters
        price_range = Product.objects.aggregate(min_price=models.Min('price'),max_price=models.Max('price'))

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
            'tags': Tag.objects.all(),
            'search_query': filters['search'],
            'selected_category': filters['category'],
            'selected_brand': filters['brand'],
            'selected_tag': filters['tag'],
            'sort_by': filters['sort_by'],
            'min_price_filter': filters['min_price'] or price_range['min_price'],
            'max_price_filter': filters['max_price'] or price_range['max_price'],
            'items_per_page': self.get_paginate_by(None),
            'view_mode': filters['view_mode'],
            'sort_options': self.sort_options,
            'items_per_page_options': self.items_per_page_options,
            'global_min_price': price_range['min_price'],
            'global_max_price': price_range['max_price'],
            'products': products,
            'is_paginated': products.has_other_pages(),

        })
        
        return context



