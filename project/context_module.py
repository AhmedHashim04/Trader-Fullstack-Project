from product.models import Category
from cart.cart import Cart as cart_branch

def contexts(request):
    contextCategories = Category.objects.filter(CATparent=None)
    contextProfile = getattr(request.user, 'profile', None)
    contextCart = cart_branch(request)
    
    if contextProfile:
        user_love = contextProfile.PRFlove.all()

        return {'contextCategories' : contextCategories, 
                "profile" : contextProfile,
                "user_love" : user_love,
                "Contextcart" : contextCart.cart.keys(),
                "total_cart_price" : contextCart.get_total_price(),
                "total_cart_items" : len(contextCart.cart),
                }
        
    return {'contextCategories' : contextCategories, 
                "profile" : contextProfile,
                }

