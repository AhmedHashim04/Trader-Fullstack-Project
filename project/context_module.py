from product.models import Category
from cart.cart import Cart as cart_branch
from account.models import Profile

def contexts(request):
    categories = Category.objects.filter(parent=None)
    profile = Profile.objects.get(user=request.user)
    cart = cart_branch(request)
    
    if profile:
        wishlist = profile.wishlist.all()

        return {
                "contextCategories" : categories, 
                "contextProfile" : profile,
                "contextWishlist" : wishlist,
                "contextCart" : cart.cart.keys(),
                "total_cart_price" : cart.get_total_price(),
                "total_cart_items" : len(cart.cart),
                }
        
    return {'contextCategories' : categories, 
                "contextProfile" : profile,
                }

