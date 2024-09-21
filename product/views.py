from typing import Any
from django.shortcuts import render ,redirect ,get_object_or_404
from django.views.generic import ListView ,DetailView
from .models import *
from accounts.models import Profile
from .form import ReviewForm

# Create your views here.
class ProductsView(ListView):
    model = Product
    context_object_name = 'all_products'
    template_name='product/products.html'
    
    
        # تعديل context ليتضمن بيانات من موديلات أخرى
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # جلب الـ context الافتراضي
        context['categories'] = Category.objects.filter(CATparent=None)  # إضافة بيانات من موديل آخر
        context['alternatives'] = Alternative.objects.all()  # إضافة بيانات من موديل آخر
        return context

    

class ProductViewDetail(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReviewForm() 
        context['reviews'] = Review.objects.filter(REVproduct=self.get_object() )
    
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object() 
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.REVuser = request.user
            review.REVproduct = product 
            review.save()
            return redirect(product.get_absolute_url())  
        return self.render_to_response(self.get_context_data(form=form))  
    
        
    
    

def add_remove_love(request,product_id):
    product = Product.objects.get(id=product_id)
    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if user in product.PRDlove.all() :
        product.PRDlove.remove(user)
    
    else:
        product.PRDlove.add(user)
        
    return redirect('product:products_list')
    
def add_remove_cart(request,product_id):
    product = Product.objects.get(id=product_id)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if user in product.PRDcart.all() :
        product.PRDcart.remove(user)
        
    else:
        
        product.PRDcart.add(user)
        
    return redirect('product:products_list')
    
def user_see_product(request,product_id):
    product = Product.objects.get(id=product_id)

    user = get_object_or_404(Profile, PRFuser=request.user)
    
    if user not in product.PRDview.all() :
        product.PRDcart.add(user)

    return redirect('product:products_list')
    

    