from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.urls import reverse



# Create your models here.
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

# class Collection(models.Model):
#     name = models.CharField(max_length=40)
#     desc  = models.TextField(_("Collection description"),max_length=1000,blank=True, null=True)
#     slug = models.SlugField(unique=True, blank=True, null=True)
#     products = models.ManyToManyField('Product', verbose_name=_("Products"), blank=True)

#     def get_absolute_url(self):
#         return reverse('settings:collection_detail', kwargs={'slug': self.slug})

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(f'collection-{self.name}')
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name