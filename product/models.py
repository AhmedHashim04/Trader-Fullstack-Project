from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib.auth.models import User


class Product(models.Model):
    PRDname     = models.CharField(max_length=40,verbose_name= _("Name") )
    PRDcategory = models.ForeignKey('Category',on_delete=models.PROTECT,verbose_name=_("Product Category"),blank=True, null=True)
    PRDBrand    = models.ForeignKey('settings.Brand',on_delete=models.PROTECT,verbose_name=_("Product Brand"),blank=True, null=True)
    PRDvariant  = models.ForeignKey('settings.Variant',on_delete=models.PROTECT,verbose_name=_("Product Variant"),blank=True, null=True)
    PRDdesc     = models.TextField(_("Description"), max_length=1000)
    PRDprice    = models.DecimalField(max_digits=20,decimal_places=2,verbose_name=_("Price"))
    PRDcost     = models.DecimalField(max_digits=20,decimal_places=2,verbose_name=_('Cost'))
    PRDcreated  = models.DateTimeField(auto_now=True)
    PRDimage    = models.ForeignKey("ProductImage",on_delete=models.PROTECT,verbose_name=_("Product Image"),blank=True, null=True)
    
    PRDview     = models.ManyToManyField("accounts.profile", verbose_name=_("User see It"),related_name="users_see_it" , blank=True )


    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.PRDname
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering  = ['-PRDcreated']
    
class ProductImage(models.Model):
    PIMGproduct = models.ForeignKey(Product,on_delete=models.PROTECT,verbose_name=_("Product"),blank=True, null=True)
    PIMGimage   = models.ImageField(_("Product Image"), upload_to='products/', height_field=None, width_field=None, max_length=None)

    
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'ProductImages'

class Category(models.Model):
    CATname  = models.CharField(_("Category Name"),max_length=50)
    CATparent = models.ForeignKey('self',limit_choices_to={'CATparent__isnull':True},on_delete=models.CASCADE,verbose_name=_("Category Parent"),blank=True, null=True)
    CATdesc  = models.TextField(_("Category Description"), max_length=1000)
    CATimage   = models.ImageField(_("Category Image"), upload_to=None, height_field=None, width_field=None, max_length=None)

    def __str__(self) -> str:
        return self.CATname
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Alternative(models.Model):
    ALTproduct          = models.ForeignKey (Product , on_delete = models.PROTECT,related_name="name_product")
    ALTalternatives     = models.ManyToManyField (Product ,related_name="ALTproducts" )
    
    
    class Meta:
        verbose_name = 'Alternative'
        verbose_name_plural = 'Alternatives'
                
class Review(models.Model):
    rate_choices = [(1,1),(2,2),(3,3),(4,4),(5,5)]
    REVcontent    = models.TextField(_("Product Review"),max_length=1000)
    REVproduct    = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="product_review")
    REVuser       = models.ForeignKey(User,on_delete=models.PROTECT,related_name="user_review")
    REVrating     = models.IntegerField(choices=rate_choices,default=3)
    REVcreated_at = models.DateTimeField(auto_now_add=True)
