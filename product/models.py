from typing import Iterable
from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.db.models import Avg
from django.utils import timezone

class Product(models.Model):

    PRDname     = models.CharField(max_length=40,verbose_name= _("Name") )
    PRDcategory = models.ForeignKey('Category',on_delete=models.PROTECT,verbose_name=_("Product Category"),blank=True, null=True)
    PRDBrand    = models.ForeignKey('settings.Brand',on_delete=models.PROTECT,verbose_name=_("Product Brand"),blank=True, null=True)
    PRDdesc     = models.TextField(_("Description"), max_length=1000)
    PRDprice    = models.DecimalField(max_digits=20,decimal_places=2,verbose_name=_("Price"))
    PRDcost     = models.DecimalField(max_digits=20,decimal_places=2,verbose_name=_('Cost'))
    PRDcreated  = models.DateTimeField(auto_now=True)
    PRDimage    = models.ForeignKey("ProductImage",on_delete=models.PROTECT,verbose_name=_("Product Image"),blank=True, null=True)
    # PRDimage    = models.ForeignKey("ProductImage",on_delete=models.PROTECT,verbose_name=_("Product Image"),blank=True, null=True)
    PRDimage   = models.ImageField(_("Product Image"), upload_to='products/', height_field=None, width_field=None, max_length=None)
    PRDslug     = models.SlugField(unique=True,blank=True, null=True)
    PRDview     = models.ManyToManyField("accounts.profile", verbose_name=_("User see It"),related_name="users_see_it" , blank=True )
    PRDtags     = TaggableManager()
    PRDstock   = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    
    overall_rating = models.FloatField(default=0.0)  

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.PRDslug})

    @staticmethod
    def calculate_overall_rating(reviews):
        if not reviews.exists():
            return 0  
        total_rating = sum(review.REVrating for review in reviews)  
        num_reviews = reviews.count()  
        return total_rating / num_reviews

    def __str__(self) -> str:
        return self.PRDname
    
    def save(self, *args, **kwargs):
        if not self.PRDslug:
            self.PRDslug = slugify(self.PRDname)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering  = ['-PRDcreated']
    
    def update_overall_rating(self):
        reviews = self.product_review.all()
        if reviews:
            self.overall_rating = round(reviews.aggregate(Avg('REVrating'))['REVrating__avg'], 2)
        else:
            self.overall_rating = 0
        self.save()

    def is_in_stock(self):
        return self.PRDstock > 0

# class ProductImage(models.Model):
#     PIMGproduct = models.ForeignKey(Product,on_delete=models.PROTECT,verbose_name=_("Product"),blank=True, null=True)
#     PIMGimage   = models.ImageField(_("Product Image"), upload_to='products/', height_field=None, width_field=None, max_length=None)

    
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'ProductImages'

class Category(models.Model):
    CATname        = models.CharField(_("Category Name"),max_length=50)
    CATparent      = models.ForeignKey('self',limit_choices_to={'CATparent__isnull':True},on_delete=models.CASCADE,verbose_name=_("Category Parent"),blank=True, null=True)
    CATdesc        = models.TextField(_("Category Description"), max_length=1000)
    CATimage       = models.ImageField(_("Category Image"), upload_to='category_pictures/', height_field=None, width_field=None, max_length=None)
    CATslug        = models.SlugField(unique=True,blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.CATslug:
            self.CATslug = slugify(self.CATname)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.CATslug})

    def __str__(self) -> str:
        return self.CATname
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Review(models.Model):
    rate_choices = [(1,1),(2,2),(3,3),(4,4),(5,5)]
    REVcontent    = models.TextField(_("Product Review"),max_length=1000)
    REVproduct    = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="product_review")
    REVuser       = models.ForeignKey(User,on_delete=models.PROTECT,related_name="user_review")
    REVrating     = models.IntegerField(choices=rate_choices,default=3)
    REVcreated_at = models.DateTimeField(auto_now_add=True)
# class Alternative(models.Model):
#     ALTproduct          = models.ForeignKey (Product , on_delete = models.PROTECT,related_name="name_product")
#     ALTalternatives     = models.ManyToManyField (Product ,related_name="ALTproducts" )
    
    
#     class Meta:
#         verbose_name = 'Alternative'
#         verbose_name_plural = 'Alternatives'
