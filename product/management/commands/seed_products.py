from django.core.management.base import BaseCommand
from product.models import Product, Category, Review
from settings.models import Brand
from django.utils.text import slugify
from django.utils import timezone
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed products into the database'

    def handle(self, *args, **options):
        # Step 1: Delete existing data
        self.stdout.write("Deleting existing data...")
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        # Step 2: Create dummy categories
        self.stdout.write("Creating categories...")
        categories = []
        for name in ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Toys', 'Health', 'Beauty', 'Grocery', 'Jewelry']:
            category = Category.objects.create(
                name=name,
                description=f"This is the {name} category.",
                slug=slugify(name)
            )
            categories.append(category)


        # Step 3: Create dummy brands
        self.stdout.write("Creating brands...")
        brands = []
        for name in ['Samsung', 'Apple', 'Sony', 'LG', 'Adidas', 'Nike', 'HP', 'Canon', 'Huawei', 'Asus', 'Microsoft', 'Google']:
            brand = Brand.objects.create(
                name=name,
                desc=f"{name} is a well-known brand.",
                slug=slugify(name)
            )
            brands.append(brand)

        # Step 3: Create dummy categories and link them to the brands
        self.stdout.write("Creating categories...")
        categories = []
        for name in ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Toys', 'Health', 'Beauty', 'Grocery', 'Jewelry']:
            category = Category.objects.create(
                name=name,
                description=f"This is the {name} category.",
                slug=slugify(name)
            )
            categories.append(category)

        # Step 4: Create dummy products and link them to the brands and categories
        self.stdout.write("Creating products...")
        for i in range(50):  # Create 50 products
            brand = random.choice(brands)
            category = random.choice(categories)
            name = f"{brand.name} {random.choice(['Galaxy', 'iPhone', 'Xperia', 'Mate', 'Surface', 'Pixel', 'TV', 'Laptop', 'Shoes', 'Clothes', 'Book', 'Toy', 'Tool', 'Accessory', 'Device'])} {random.randint(100, 1000)}"
            price = Decimal(random.randint(100, 1000))
            stock = random.randint(0, 100)
            description = f"This is a description for {name}. It belongs to the {category.name} category and is manufactured by {brand.name}."
            image_url = f"https://via.placeholder.com/400?text={slugify(name)}"

            product = Product.objects.create(
                name=name,
                category=category,
                brand=brand,
                description=description,
                price=price,
                stock=stock,
                image=image_url,
                slug=slugify(name),
                created_at=timezone.now()
            )

            # Step 5: Create dummy reviews for each product
            for _ in range(random.randint(1, 5)):  # Each product gets 1-5 reviews
                Review.objects.create(
                    product=product,
                    user_id=1,  # Assuming user IDs exist from 1 to 10
                    content=f"This is a review for {product.name}.",
                    rating=random.randint(1, 5),
                    created_at=timezone.now()
                )

        self.stdout.write(self.style.SUCCESS("Products seeded successfully!"))
