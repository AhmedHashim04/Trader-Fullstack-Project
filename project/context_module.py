from product.models import Category
from cart.cart import Cart as cart_branch
from account.models import Profile
from features.models import Brand

def contexts(request):
    categories = Category.objects.filter(parent=None)
    brands = Brand.objects.filter()
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user.id)
        cart = cart_branch(request)
        if profile:
            wishlist = profile.wishlist.all()

            return {
                    "contextCategories" : categories, 
                    "contextBrands" : brands,
                    "contextProfile" : profile,
                    "contextWishlist" : wishlist,
                    "contextCart" : cart.cart.keys(),
                    "total_cart_price" : cart.get_total_price(),
                    "total_cart_items" : len(cart.cart),
                    }
            
        return {'contextCategories' : categories, 
                "contextProfile" : profile,
                    }

    return {'contextCategories' : categories,
            "contextBrands" : brands,}

