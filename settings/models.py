from django.db import models
from django.utils.translation import gettext as _


# Create your models here.
class Brand(models.Model):
    BRDname  = models.CharField(max_length=40)
    BRDdesc  = models.TextField(_("Brand description"),max_length=1000,blank=True, null=True)
    
    def __str__(self) -> str:
        return self.BRDname
    
    
class Variant(models.Model):
    VARname = models.CharField(max_length=40)
    VARdesc  = models.TextField(_("Variant description"),max_length=1000,blank=True, null=True)