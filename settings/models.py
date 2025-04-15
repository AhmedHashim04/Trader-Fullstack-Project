from django.db import models
from django.utils.translation import gettext as _


# Create your models here.
class Brand(models.Model):
    name  = models.CharField(max_length=40)
    desc  = models.TextField(_("Brand description"),max_length=1000,blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name
    
    
class Variant(models.Model):
    name = models.CharField(max_length=40)
    desc  = models.TextField(_("Variant description"),max_length=1000,blank=True, null=True)