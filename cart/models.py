from django.db import models
from product.models import Product
from django.contrib.auth.models import User

class CartModel(models.Model):
    CRTuser = models.ForeignKey(User, on_delete=models.CASCADE)
    CRTproduct = models.ForeignKey(Product, on_delete=models.CASCADE)
    CRTquantity = models.IntegerField(default=1)
    CRTcreated_at = models.DateTimeField(auto_now_add=True)
    CRTupdated_at = models.DateTimeField(auto_now=True)
    CRTslug = models.SlugField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.CRTuser.username} - {self.CRTproduct.name}"
    
    def get_total_price(self):
        return self.CRTquantity * self.CRTproduct.price
    
    # def get_total_price_after_discount(self):
    #     return self.get_total_price() - self.get_discount()
    
    # def get_discount(self):
    #     return 0
