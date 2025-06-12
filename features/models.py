from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.urls import reverse
from product.models import Product

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Brand(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    name  = models.CharField(max_length=40)
    logo = models.ImageField(upload_to='brand_pictures/', verbose_name=_("Image"), blank=True, null=True)
    desc  = models.TextField(_("Brand description"),max_length=1000,blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('settings:brand_detail', kwargs={'slug': self.slug})
class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    products = models.ManyToManyField('product.Product', related_name='collections')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"

    def __str__(self):
        return self.name



# class Variant(models.Model):
#     name = models.CharField(max_length=40)
#     desc  = models.TextField(_("Variant description"),max_length=1000,blank=True, null=True)
#     slug = models.SlugField(unique=True, blank=True, null=True)

#     def __str__(self):
#         return self.name
    
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)
