from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from product.models import Product  # استيراد نموذج Product

# Create your models here.

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    ORDuser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    ORDcreated_at = models.DateTimeField(default=timezone.now)
    ORDupdated_at = models.DateTimeField(auto_now=True)
    ORDstatus = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    ORDtotal_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f" {self.id} - {self.ORDuser.username}"

    def get_items(self):
        return self.items.all()

class OrderItem(models.Model):
    OITEMorder = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    OITEMproduct = models.ForeignKey(Product, on_delete=models.CASCADE)
    OITEMquantity = models.PositiveIntegerField(default=1)
    OITEMprice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.OITEMquantity} x {self.OITEMproduct.PRDname} in {self.OITEMorder.id}"
    
    def get_total_price(self):
        return self.OITEMprice * self.OITEMquantity



