from django.core.management.base import BaseCommand
from product.models import Product, Review, Tag, Category
from features.models import Brand, ProductImage, Collection

class Command(BaseCommand):
    help = "Deletes all product-related data (products, images, reviews, tags, categories, brands, collections)."

    def handle(self, *args, **kwargs):
        print("🧹 Deleting ProductImages...")
        ProductImage.objects.all().delete()

        print("🧹 Deleting Reviews...")
        Review.objects.all().delete()

        print("🧹 Deleting Products...")
        Product.objects.all().delete()

        print("🧹 Deleting Tags...")
        Tag.objects.all().delete()

        print("🧹 Deleting Categories...")
        Category.objects.all().delete()

        print("🧹 Deleting Brands...")
        Brand.objects.all().delete()

        print("🧹 Deleting Collections...")
        Collection.objects.all().delete()

        print("✅ All product-related data has been deleted.")
