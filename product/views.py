from typing import Any
from django.db.models.base import Model as Model
from django.shortcuts import redirect ,get_object_or_404 
from django.http import HttpResponseRedirect
from django.contrib import messages


from django.views.generic import ListView ,DetailView
from .models import *
from accounts.models import Profile
from .form import ReviewForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# Create your views here.
class ProductsView(ListView):
    model = Product
    context_object_name = 'all_products'  # اسم السياق الذي ستحصل عليه في القالب
    template_name = 'product/products.html'
    paginate_by = 2  # عدد العناصر في كل صفحة

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # حساب الـ overall rating لكل منتج
        for product in context['all_products']:
            reviews = Review.objects.filter(REVproduct=product)
            product.overall_rating = Product.calculate_overall_rating(reviews)

        return context

class ProductViewDetail(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = "PRDslug"
    slug_url_kwarg = "slug"

    def calculate_overall_rating(self, reviews):
        if not reviews.exists():
            return 0  # إذا لم يكن هناك أي تقييمات

        # احسب مجموع التقييمات
        total_rating = sum([review.REVrating for review in reviews])

        # احسب عدد التقييمات
        num_reviews = reviews.count()

        # ارجع النتيجة مقربة إلى منزلتين عشرية
        return round(total_rating / num_reviews, 1)

    def get_context_data(self, **kwargs):
        # الحصول على المستخدم الحالي
        user_profile = Profile.objects.get(PRFuser=self.request.user)

        # المنتجات في السلة والحب للمستخدم الحالي
        cart_products = user_profile.PRFcart.all()
        love_products = user_profile.PRFlove.all()

        context = super().get_context_data(**kwargs)
        context['form']             = ReviewForm()
        context['reviews']          = Review.objects.filter(REVproduct=self.get_object())
        context['overall_rating']   = self.calculate_overall_rating(context['reviews'])

        context['in_cart'] = self.get_object() in cart_products
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
            messages.success(self.request, 'ٌReview , Rating had sent  Successfuly !')
            return redirect(product.get_absolute_url())

        return self.render_to_response(self.get_context_data(form=form))
 

class CategorysView(ListView):
    model = Category
    context_object_name = 'all_categories'
    template_name='product/categories.html'
    paginate_by = 1


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
    
class CartViewDetail(DetailView):
    model = Profile
    template_name = 'product/cart.html'
    context_object_name = 'profile'
    slug_field     = "PRFslug"
    slug_url_kwarg = "slug"
    
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart_products=Profile.objects.filter(PRFuser=self.request.user)[0].PRFcart.all()
        context["total_price"] = sum([i.PRDprice for i in cart_products])
        return context

@login_required
def add_remove_love(request,slug):
    product = Product.objects.get(PRDslug=slug)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if product in user.PRFlove.all() :
        user.PRFlove.remove(product)
        messages.success(request, 'Product had Removed from Wishlist !')
    else:
        user.PRFlove.add(product)
        messages.success(request, 'Product in Wishlist Now !')


    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_remove_cart(request,slug):
    product = Product.objects.get(PRDslug=slug)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if product in user.PRFcart.all() :
        user.PRFcart.remove(product)
        messages.success(request, 'Product had Removed from Cart !')

    else:
        user.PRFcart.add(product)
        messages.success(request, 'Product in Cart Now !')
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


    
def user_see_product(request,slug):
    product = Product.objects.get(PRDslug=slug)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if user not in product.PRDview.all() :
        product.PRDview.add(user)

    return redirect(product.get_absolute_url())  