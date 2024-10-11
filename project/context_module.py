from product.models import  Category

def contexts(request):
    contextCategories = Category.objects.filter(CATparent=None)
    contextProfile = getattr(request.user, 'profile', None)
    
    if contextProfile:
        user_cart = contextProfile.PRFcart.all()
        user_love = contextProfile.PRFlove.all()

        return {'contextCategories' : contextCategories, 
                "profile" : contextProfile,
                "user_cart" : user_cart,
                "user_love" : user_love,
                }
        
    return {'contextCategories' : contextCategories, 
                "profile" : contextProfile,
                }