from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from product.models import Product
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
import uuid
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=(('fixed', 'Fixed'), ('percent', 'Percent')))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now() + timedelta(days=30))
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  
    used_count = models.PositiveIntegerField(default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and (self.usage_limit is None or self.used_count < self.usage_limit)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')
class Brand(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    name  = models.CharField(max_length=40)
    logo = models.ImageField(upload_to='brand_pictures/', verbose_name=_("Image"), blank=True, null=True)
    desc  = models.TextField(_("Brand description"),max_length=1000,blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    products = models.ManyToManyField('product.Product', related_name='collections')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Profile(models.Model):
    id             = models.UUIDField(_("ID"), primary_key=True, editable=False , default=uuid.uuid4)
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile" ,verbose_name=_("User"))
    email          = models.EmailField(max_length=100, verbose_name=_("Email"))
    phone_number   = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    address        = models.CharField(validators=[RegexValidator(regex=r'^[\u0600-\u06FF\s\d]+(?:\s[\u0600-\u06FF\s\d]+)*$',message="Enter a valid Egyptian Address in Arabic")],max_length=255,verbose_name=_("Address"),blank=True,null=True)
    CITY_CHOICES = [('الجيزة', 'الجيزة'),('القاهرة', 'القاهرة'),('الاسماعيلية', 'الاسماعيلية'),('الفيوم', 'الفيوم'),('المنيا', 'المنيا'),('المنوفية', 'المنوفية'),('الوادي الجديد', 'الوادي الجديد'),('القليوبية', 'القليوبية'),('الشرقية', 'الشرقية'),('الغربية', 'الغربية'),('الدقهلية', 'الدقهلية'),('الدمياط', 'الدمياط'),('البحرالاحمر', 'البحرالاحمر'),]
    city= models.CharField(choices=CITY_CHOICES,max_length=100,verbose_name=_("City"),blank=True,null=True)
    country        = models.CharField(choices=[('مصر', 'مصر')],max_length=100,verbose_name=_("Country"),blank=True,null=True)
    postal_code    = models.CharField(validators=[RegexValidator(regex=r'^(?:[1-9]\d{2}|[1-9]\d{4})$',message="Enter a valid Egyptian Postal Code")],max_length=10,verbose_name=_("Postal Code"),blank=True,null=True)
    profile_image  = models.ImageField(upload_to='profile_pictures/', verbose_name=_("Profile Image"), blank=True, null=True)
    date_of_birth  = models.DateField(blank=True, null=True, verbose_name=_("Date of Birth"))
    wishlist       = models.ManyToManyField(Product, verbose_name=_("Wishlist"), related_name="wishlist", blank=True)
    activation_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Activation Key"))
    date_joined    = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Joined"))
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
class Tag(models.Model):
    key = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class Product(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name=_("Tags"), blank=True)
    trending = models.BooleanField(default=False, verbose_name=_("Trending"), help_text=_("Is this product trending?"))
    name = models.CharField(max_length=40, verbose_name=_("Name"))
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name=_("Category"), blank=True, null=True)
    brand = models.ForeignKey('features.Brand', on_delete=models.PROTECT, verbose_name=_("Brand"), blank=True, null=True)
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Price"))
    cost = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Cost") , blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created At"))
    image = models.ImageField(upload_to='products/', verbose_name=_("Product Image"), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    viewed_by = models.ManyToManyField("account.Profile", verbose_name=_("Viewed By"), related_name="viewed_products", blank=True)
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    overall_rating = models.FloatField(default=0.0, verbose_name=_("Overall Rating"))
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    parent = models.ForeignKey('self', limit_choices_to={'parent__isnull': True}, on_delete=models.CASCADE, verbose_name=_("Parent Category"), blank=True, null=True)
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    image = models.ImageField(upload_to='category_pictures/', verbose_name=_("Image"), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_review", verbose_name=_("Product"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_review", verbose_name=_("User"))
    content = models.TextField(max_length=1000, verbose_name=_("Review"),default="")
    rating = models.IntegerField(choices=RATING_CHOICES, default=3, verbose_name=_("Rating"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))