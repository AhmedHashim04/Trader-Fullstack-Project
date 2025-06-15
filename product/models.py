from django.db import models
from django.db.models import Avg, UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Tag(models.Model):
    key = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Color"), help_text=_("Text color for tag (e.g. #fff or 'red')"))
    bg_color = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Background Color"), help_text=_("Background color for tag (e.g. #000 or 'blue')"))

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=40,verbose_name=_("Name"),db_index=True)
    category = models.ForeignKey('Category',on_delete=models.PROTECT,verbose_name=_("Category"),blank=True,null=True,related_name='products')
    brand = models.ForeignKey('features.Brand',on_delete=models.PROTECT,verbose_name=_("Brand"),blank=True,null=True,related_name='products')
    description = models.TextField(max_length=1000,verbose_name=_("Description"))
    price = models.DecimalField(max_digits=20,decimal_places=2,verbose_name=_("Price"),validators=[MinValueValidator(0)])
    cost = models.DecimalField(max_digits=20,decimal_places=2,verbose_name=_("Cost"),blank=True,null=True,validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_("Created At"),db_index=True)
    updated_at = models.DateTimeField(auto_now=True,verbose_name=_("Updated At"))
    image = models.ImageField(upload_to='products/',verbose_name=_("Product Image"),blank=True,null=True)
    slug = models.SlugField(unique=True,blank=True,null=True,max_length=255,db_index=True)
    stock = models.PositiveIntegerField(default=0,verbose_name=_("Stock"),validators=[MinValueValidator(0)])
    overall_rating = models.FloatField(default=0.0,verbose_name=_("Overall Rating"),editable=False)
    is_available = models.BooleanField(default=True,verbose_name=_("Is Available"),db_index=True)
    discount = models.DecimalField(max_digits=5,decimal_places=2,default=0,verbose_name=_("Discount"),help_text=_("Discount percentage (0-100)"),validators=[MinValueValidator(0), MaxValueValidator(100)])
    trending = models.BooleanField(default=False,verbose_name=_("Trending"),help_text=_("Is this product trending?"),db_index=True)
    tags = models.ManyToManyField('Tag',verbose_name=_("Tags"),blank=True,related_name='products')
    viewed_by = models.ManyToManyField("account.Profile",verbose_name=_("Viewed By"),related_name="viewed_products",blank=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-overall_rating'], name='rating_idx'),
            models.Index(fields=['category', 'brand'], name='category_brand_idx'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:product_detail', kwargs={'slug': self.slug})

    @property
    def price_after_discount(self):
        """Calculate discounted price with tax-safe decimal operations"""
        return self.price * (100 - self.discount) / 100

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def has_discount(self):
        return self.discount > 0

    def update_rating(self):
        """Update rating aggregation using efficient database query"""
        result = self.reviews.aggregate(average_rating=Avg('rating'))
        self.overall_rating = round(result['average_rating'] or 0, 2)
        self.save(update_fields=['overall_rating'])


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="reviews",verbose_name=_("Product"))
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,related_name="reviews",verbose_name=_("User"))
    content = models.TextField(max_length=1000,verbose_name=_("Review"),default="")
    rating = models.IntegerField(choices=RATING_CHOICES,default=3,verbose_name=_("Rating"))
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_("Created At"),db_index=True)
    updated_at = models.DateTimeField(auto_now=True,verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        constraints = [
            UniqueConstraint(
                fields=['product', 'user'],
                name='unique_product_review')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating asynchronously (consider using signals + Celery)
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_rating()

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    parent = models.ForeignKey('self', limit_choices_to={'parent__isnull': True}, on_delete=models.CASCADE, verbose_name=_("Parent Category"), blank=True, null=True)
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    image = models.ImageField(upload_to='category_pictures/', verbose_name=_("Image"), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:category_detail', kwargs={'slug': self.slug})



    # ("new", _("New")),
    # ("best", _("Best")),
    # ("sale", _("Sale")),
    # ("summer", _("Summer")),
    # ("winter", _("Winter")),
    # ("spring", _("Spring")),
    # ("autumn", _("Autumn")),
    # ("limited", _("Limited")),
    # ("recommended", _("Recommended")),
    # ("gift", _("Gift")),
    # ("popular", _("Popular")),
    # ("top", _("Top")),
    # ("exclusive", _("Exclusive")),
    # ("special", _("Special")),
    # ("new_arrivals", _("New Arrivals")),
    # ("best_sellers", _("Best Sellers")),
    # ("on_sale", _("On Sale")),
    # ("summer_collection", _("Summer Collection")),
    # ("winter_collection", _("Winter Collection")),
    # ("spring_collection", _("Spring Collection")),
    # ("autumn_collection", _("Autumn Collection")),
    # ("limited_collection", _("Limited Collection")),
    # ("recommended_collection", _("Recommended Collection")),
    # ("gift_collection", _("Gift Collection")),
    # ("popular_collection", _("Popular Collection")),
    # ("top_collection", _("Top Collection")),
    # ("exclusive_collection", _("Exclusive Collection")),
    # ("special_collection", _("Special Collection")),
    # ("new_arrivals_collection", _("New Arrivals Collection")),
    # ("best_sellers_collection", _("Best Sellers Collection")),
    # ("on_sale_collection", _("On Sale Collection")),