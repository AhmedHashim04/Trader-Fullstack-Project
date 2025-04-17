from django.db import models
from django.utils.translation import gettext as _
# from django.db.models.signals import pre_save
from django.utils.text import slugify



# Create your models here.
class Brand(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    name  = models.CharField(max_length=40)
    desc  = models.TextField(_("Brand description"),max_length=1000,blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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
