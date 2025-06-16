from django.core.management.base import BaseCommand
from product.models import Product, Review, Tag, Category
from features.models import Brand, ProductImage, Collection
from order.models import Order, OrderItem, Address
from coupon.models import Coupon, CouponUsage
# from payment.models import Payment

class Command(BaseCommand):
    help = "Deletes all product-related data (products, images, reviews, tags, categories, brands, collections ..)."

    def handle(self, *args, **kwargs):
        print("🧹 Deleting Coupons...")
        Coupon.objects.all().delete()
        CouponUsage.objects.all().delete()

        # print("🧹 Deleting Payments...")
        # Payment.objects.all().delete()

        print("🧹 Deleting Orders...")
        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        print("🧹 Deleting Addresses...")
        Address.objects.all().delete()

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
