from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from product.models import Product
import uuid

class Profile(models.Model):
    id = models.UUIDField(_("ID"), primary_key=True, editable=False , default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.EmailField(max_length=100, verbose_name=_("Email"))
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_("Date Joined"))
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    address = models.TextField(max_length=255, verbose_name=_("Address"), blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name=_("Country"), blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"), blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name=_("Profile Image"))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("Date of Birth"))
    wishlist = models.ManyToManyField(Product, verbose_name=_("Favorite Products"), related_name="loved_by_users", blank=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def wishlist_count(self):
        return self.wishlist.count()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
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
    
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.db.models import Avg

class Product(models.Model):
    name = models.CharField(max_length=40, verbose_name=_("Name"))
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name=_("Category"), blank=True, null=True)
    brand = models.ForeignKey('settings.Brand', on_delete=models.PROTECT, verbose_name=_("Brand"), blank=True, null=True)
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Price"))
    cost = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Cost"))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created At"))
    # image = models.ImageField(upload_to='products/', verbose_name=_("Product Image"), blank=True, null=True)
    image = models.URLField(verbose_name=_("Image URL"), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    viewed_by = models.ManyToManyField("account.Profile", verbose_name=_("Viewed By"), related_name="viewed_products", blank=True)
    tags = TaggableManager(verbose_name=_("Tags"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    overall_rating = models.FloatField(default=0.0, verbose_name=_("Overall Rating"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:product_detail', kwargs={'slug': self.slug})

    def is_in_stock(self):
        return self.stock > 0

    def update_overall_rating(self) -> None:
        reviews = self.product_review.all()
        if reviews.exists():
            try:
                average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
                self.overall_rating = round(average_rating, 2) if average_rating is not None else 0
            except TypeError:
                self.overall_rating = 0
        else:
            self.overall_rating = 0
        self.save()

    @classmethod
    def calculate_overall_rating(cls, reviews: models.QuerySet['Review']) -> float:
        if not reviews.exists():
            return 0
        total_rating = sum(review.rating for review in reviews)
        return total_rating / reviews.count()


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


from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
import random

from product.models import Product, Category
from settings.models import Brand  # تأكد من المسار حسب مشروعك

class Command(BaseCommand):
    help = 'Seed the database with dummy products, categories, and brands'

    def handle(self, *args, **kwargs):
        fake = Faker()

        self.stdout.write(self.style.SUCCESS('Seeding categories...'))
        categories = []
        for i in range(10):
            name = f"{fake.word().capitalize()} Category {i+1}"
            category = Category.objects.create(
                name=name,
                description=fake.text(max_nb_chars=100),
                slug=slugify(name)
            )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS('Seeding brands...'))
        brands = []
        for i in range(9):
            name = f"{fake.company()} Brand {i+1}"
            brand = Brand.objects.create(
                name=name,
                description=fake.text(max_nb_chars=100),
                slug=slugify(name)
            )
            brands.append(brand)

        self.stdout.write(self.style.SUCCESS('Seeding products...'))
        for i in range(40):
            name = f"{fake.word().capitalize()} Product {i+1}"
            product = Product.objects.create(
                name=name,
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(100, 1000), 2),
                cost=round(random.uniform(50, 500), 2),
                stock=random.randint(10, 100),
                category=random.choice(categories),
                brand=random.choice(brands),
                slug=slugify(name),
                image=fake.image_url(),
                overall_rating=round(random.uniform(1, 5), 2),
            )
            product.tags.add(*[fake.word() for _ in range(3)])

        self.stdout.write(self.style.SUCCESS('✅ Database seeding completed.'))
