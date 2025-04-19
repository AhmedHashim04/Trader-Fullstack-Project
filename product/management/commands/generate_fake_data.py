from django.core.management.base import BaseCommand
from faker import Faker
import random
import uuid
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.contrib.auth.models import User

from account.models import Profile
from product.models import Product, Category
from settings.models import Brand
from cart.models import CartModel

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake e-commerce data (users, products, brands, categories, carts, images...)'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--products', type=int, default=20, help='Number of products to create')
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create')
        parser.add_argument('--brands', type=int, default=5, help='Number of brands to create')

    def handle(self, *args, **options):
        num_users = options['users']
        num_products = options['products']
        num_categories = options['categories']
        num_brands = options['brands']

        self.stdout.write(f"🚀 Starting to generate: {num_users} users, {num_products} products, {num_categories} categories, {num_brands} brands")

        categories = self.create_categories(num_categories)
        brands = self.create_brands(num_brands)
        products = self.create_products(categories, brands, num_products)
        self.create_users(products, num_users)
        self.create_cart_items(products)

        self.stdout.write(self.style.SUCCESS("✅ Done generating fake e-commerce data."))

    def create_categories(self, n):
        categories = []
        for _ in range(n):
            name = fake.word().capitalize()
            category = Category.objects.create(
                name=name,
                description=fake.text(max_nb_chars=200),
                slug=slugify(name)
            )
            categories.append(category)
        return categories

    def create_brands(self, n):
        brands = []
        for _ in range(n):
            name = fake.company()
            brand = Brand.objects.create(
                name=name,
                desc=fake.text(max_nb_chars=200),
                slug=slugify(name)
            )
            brands.append(brand)
        return brands

    def create_products(self, categories, brands, n):
        products = []
        for _ in range(n):
            name = fake.word().capitalize() + " " + fake.word().capitalize()
            product = Product.objects.create(
                name=name,
                description=fake.text(max_nb_chars=300),
                price=round(random.uniform(10.0, 500.0), 2),
                cost=round(random.uniform(5.0, 300.0), 2),
                category=random.choice(categories),
                brand=random.choice(brands),
                image=f"https://picsum.photos/seed/{uuid.uuid4()}/300/300",
                stock=random.randint(0, 100),
                slug=slugify(name),
            )
            products.append(product)
        return products

    def create_users(self, products, n):
        for _ in range(n):
            username = fake.user_name()[:20]
            email = fake.email()
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpassword123'
            )

            profile = user.profile
            profile.email = email
            profile.phone_number = fake.phone_number()
            profile.address = fake.address()
            profile.city = fake.city()
            profile.country = fake.country()
            profile.postal_code = fake.postcode()
            profile.date_of_birth = fake.date_of_birth()

            img_url = f"https://i.pravatar.cc/150?u={uuid.uuid4()}"
            response = requests.get(img_url)
            if response.status_code == 200:
                profile.profile_image.save(f"{username}.jpg", ContentFile(response.content), save=True)
            print(f"[DEBUG] Trying to save user: {username}, length: {len(username)}")
            profile.save()

            wishlist_items = random.sample(products, random.randint(1, min(5, len(products))))
            profile.wishlist.set(wishlist_items)

    def create_cart_items(self, products):
        users = User.objects.all()
        for user in users:
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                CartModel.objects.create(
                    user=user,
                    product=product,
                    quantity=random.randint(1, 5),
                    slug=slugify(f"{user.username}-{product.name}-{uuid.uuid4()}")
                )

# python manage.py generate_fake_data --users 30 --products 50 --categories 10 --brands 8
#or
# python manage.py generate_fake_data 
