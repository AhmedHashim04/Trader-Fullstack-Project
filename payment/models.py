from django.db import models
from django.contrib.auth.models import User
from product.models import Product 
from order.models import Order
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pay_phone = models.CharField(max_length=11)
    pay_image = models.ImageField(_("PayImage"), upload_to=None, height_field=None, width_field=None, max_length=None)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.amount}"
