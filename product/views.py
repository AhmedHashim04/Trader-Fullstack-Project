from typing import Any
from django.db.models.base import Model as Model
from django.shortcuts import render ,redirect ,get_object_or_404 
from django.http import HttpResponseRedirect

from django.views.generic import ListView ,DetailView
from .models import *
from accounts.models import Profile
from .form import ReviewForm
from django.contrib.auth.decorators import login_required

# Create your views here.
class ProductsView(ListView):
    model = Product
    context_object_name = 'all_products'
    template_name='product/products.html'
    extra_context = {"is_category":False}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # جلب الـ context الافتراضي
        context['categories'] = Category.objects.filter(CATparent=None)  # إضافة بيانات من موديل آخر
        user_cart = self.request.user.profile.PRFcart.all() 
        context['user_cart'] = user_cart
        user_love = self.request.user.profile.PRFlove.all() 
        context['user_love'] = user_love
        return context

    

class CategoryViewDetail(DetailView):
    model = Category
    template_name = 'product/products.html'
    context_object_name = 'category'
    extra_context = {"is_category":True}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        obj = self.get_object()
        context['all_products'] = Product.objects.filter(PRDcategory=obj)  
        user_cart = self.request.user.profile.PRFcart.all() 
        print(user_cart)
        context['user_cart'] = user_cart
        user_love = self.request.user.profile.PRFlove.all() 
        context['user_love'] = user_love
        
        return context

class LoveViewDetail(DetailView):
    model = Profile
    template_name = 'product/love.html'
    context_object_name = 'profile'
    
    # def get_queryset(self):
    #     return Profile.objects.filter(PRFuser=self.request.user)[0].PRFlove.all()

    
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context
    
class CartViewDetail(DetailView):
    model = Profile
    template_name = 'product/cart.html'
    context_object_name = 'profile'
    
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart_products=Profile.objects.filter(PRFuser=self.request.user)[0].PRFcart.all()
        context["total_price"] = sum([i.PRDprice for i in cart_products])
        return context


class ProductViewDetail(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        cart_products=Profile.objects.filter(PRFuser=self.request.user)[0].PRFcart.all()
        love_products=Profile.objects.filter(PRFuser=self.request.user)[0].PRFlove.all()
        context = super().get_context_data(**kwargs)
        context['form'] = ReviewForm() 
        context['reviews'] = Review.objects.filter(REVproduct=self.get_object())
        context['in_cart'] = False
        context['in_love'] = False

        if self.get_object() in cart_products:
            context['in_cart'] = True
        if self.get_object() in love_products:
            context['in_love'] = True
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object() 
        form = ReviewForm(request.POST)
        print("t"*200)
        if form.is_valid():
            review = form.save(commit=False)
            review.REVuser = request.user
            review.REVproduct = product 
            review.save()
            return redirect(product.get_absolute_url())  
        return self.render_to_response(self.get_context_data(form=form))  


@login_required
def add_remove_love(request,product_id):
    product = Product.objects.get(id=product_id)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if product in user.PRFcart.all() :
        user.PRFlove.remove(product)
        
    else:
        
        user.PRFlove.add(product)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_remove_cart(request,product_id):
    product = Product.objects.get(id=product_id)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if product in user.PRFcart.all() :
        user.PRFcart.remove(product)
        
    else:
        
        user.PRFcart.add(product)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


    
def user_see_product(request,product_id):
    product = Product.objects.get(id=product_id)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if user not in product.PRDview.all() :
        product.PRDview.add(user)

    return redirect(product.get_absolute_url())  
    

    