from product.models import Category
from cart.cart import Cart as ShoppingCart
from account.models import Profile
from features.models import Brand

def contexts(request):
    categories = Category.objects.filter(parent=None)
    brands = Brand.objects.filter()
    cart = ShoppingCart(request)

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user.id)
        wishlist = profile.wishlist.all()

        return {
                    "contextCategories" : categories, 
                    "contextBrands" : brands,
                    "contextProfile" : profile,
                    "contextWishlist" : wishlist,
                    "contextCart" : cart.cart.keys(),
                    "total_cart_price" : cart.get_total_price_after_discount(),
                    "total_cart_items" : len(cart.cart.keys()),
                    }
            
                    

    return {'contextCategories' : categories,
            "contextBrands" : brands,
            "contextCart" : cart.cart.keys(),
            "total_cart_price" : cart.get_total_price_after_discount(),
            "total_cart_items" : len(cart.cart.keys()),

            }

