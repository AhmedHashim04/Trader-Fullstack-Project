from django.core.management.base import BaseCommand
from product.models import Product, Category , Review
from settings.models import Brand
import random
from decimal import Decimal
# timezone
from django.utils import timezone
from django.utils.text import slugify
class Command(BaseCommand):
    help = 'Seed products into the database'

    def handle(self, *args, **options):
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        brands = list(Brand.objects.all())
        if not brands:
            for brand_name in ["Apple", "Samsung", "Google", "Microsoft", "Lenovo", "Dell", "HP", "Asus", "Acer", "Toshiba", "LG", "Sony", "Panasonic", "Nokia", "Xiaomi"]:
                Brand.objects.create(name=brand_name, image=f"https://via.placeholder.com/150?text={brand_name}")
            brands = list(Brand.objects.all())

        category_data = [
            ("Smartphones", "All kinds of smartphones"),
            ("Laptops", "High performance laptops"),
            ("TVs", "Smart and 4K TVs"),
            ("Headphones", "Wired and wireless headphones"),
            ("Monitors", "HD and curved monitors"),
            ("Smartwatches", "Latest wearable tech"),
        ]

        categories = []
        for name, desc in category_data:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": desc},
                image=f"https://picsum.photos/seed/{slugify(name)}/600/400"
            )
            categories.append(category)

        product_names = {
            "Smartphones": ["Galaxy S23", "iPhone 14", "Xperia 5"],
            "Laptops": ["MacBook Air", "Dell XPS 13", "Lenovo ThinkPad"],
            "TVs": ["Sony Bravia", "LG OLED CX", "Samsung QLED"],
            "Headphones": ["Sony WH-1000XM5", "AirPods Pro", "Galaxy Buds"],
            "Monitors": ["Dell Ultrasharp", "LG UltraWide", "Samsung Odyssey"],
            "Smartwatches": ["Apple Watch", "Samsung Galaxy Watch", "Fitbit Sense"],
        }

        for category in categories:
            names = product_names.get(category.name, [])
            for name in names:
                brand = random.choice(brands)
                price = Decimal(random.randint(3000, 20000))
                cost = price - Decimal(random.randint(500, 1500))
                image = f"https://picsum.photos/seed/{slugify(name)}/600/400"

                Product.objects.create(
                    name=name,
                    category=category,
                    brand=brand,
                    description=f"{name} by {brand.name} in {category.name}",
                    price=price,
                    cost=cost,
                    stock=random.randint(5, 100),
                    overall_rating=round(random.uniform(3.5, 5.0), 1),
                    created_at=timezone.now(),
                    slug=slugify(name),
                    image=image,
                )

        print("Products seeded successfully.")

