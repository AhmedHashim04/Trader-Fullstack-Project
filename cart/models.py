from django.db import models
from product.models import Product
from django.contrib.auth.models import User

class CartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    def get_total_price(self):
        return self.quantity * self.product.price
    
    # def get_total_price_after_discount(self):
    #     return self.get_total_price() - self.get_discount()
    
    # def get_discount(self):
    #     return 0
