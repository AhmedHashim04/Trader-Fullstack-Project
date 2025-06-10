from django.core.management.base import BaseCommand
from product.models import Product, Category, Review, Tag
from features.models import Brand, Collection, ProductImage
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.core.files import File
from faker import Faker
from datetime import timedelta
import random
import os
import uuid
import requests
from typing import List, Optional

from coupons.models import Coupon
from account.models import Profile

User = get_user_model()
fake = Faker()

# Constants
DEFAULT_PASSWORD = "password123"
TEMP_DIR = "/tmp"
IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']


class Command(BaseCommand):
    help = 'Generate dummy data for e-commerce website'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create')
        parser.add_argument('--brands', type=int, default=5, help='Number of brands to create')
        parser.add_argument('--products', type=int, default=20, help='Number of products to create')
        parser.add_argument('--collections', type=int, default=3, help='Number of collections to create')
        parser.add_argument('--coupons', type=int, default=5, help='Number of coupons to create')
        parser.add_argument('--reviews', type=int, default=30, help='Number of reviews to create')

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS('Starting to generate dummy data...'))

        users = self.create_users(options['users'])
        categories = self.create_categories(options['categories'])
        brands = self.create_brands(options['brands'])
        products = self.create_products(options['products'], categories, brands)
        self.create_collections(options['collections'], products)
        self.create_coupons(options['coupons'])
        self.create_reviews(options['reviews'], products, users)

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))

    def download_image(self, url: str, model_name: str) -> Optional[str]:
        """Download an image from the internet and save it temporarily."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            ext = url.split('.')[-1].lower()
            if ext not in IMAGE_EXTENSIONS:
                ext = 'jpg'

            filename = f"{model_name}_{uuid.uuid4().hex[:10]}.{ext}"
            temp_file = os.path.join(TEMP_DIR, filename)

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return temp_file
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error downloading image: {e}"))
            return None

    def create_users(self, count: int) -> List[User]:
        """Create users and their profiles."""
        users = []
        for _ in range(count):
            username = fake.user_name()
            email = fake.email()

            user = User.objects.create_user(
                username=username,
                email=email,
                password=DEFAULT_PASSWORD
            )

            profile = self.create_profile(user, email)
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        return users

    def create_profile(self, user: User, email: str) -> Profile:
        """Create a profile for a user."""
        profile_image_url = fake.image_url(width=200, height=200)
        temp_image = self.download_image(profile_image_url, 'profile')

        profile = Profile.objects.get(user=user)
        profile.email = email
        profile.phone_number = fake.phone_number()
        profile.address = fake.street_address()
        profile.city = random.choice(Profile.CITY_CHOICES)[0]
        profile.country = 'Egypt'
        profile.postal_code = str(random.randint(10000, 99999))
        profile.date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)

        if temp_image:
            with open(temp_image, 'rb') as f:
                profile.profile_image.save(os.path.basename(temp_image), File(f))
            os.remove(temp_image)

        profile.save()
        return profile

    def create_categories(self, count: int) -> List[Category]:
        """Create categories."""
        categories = []
        parent_categories = self.create_parent_categories(min(3, count))

        for _ in range(count - len(parent_categories)):
            categories.append(self.create_category(parent=random.choice(parent_categories)))

        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        return categories

    def create_parent_categories(self, count: int) -> List[Category]:
        """Create parent categories."""
        return [self.create_category() for _ in range(count)]

    def create_category(self, parent: Optional[Category] = None) -> Category:
        """Create a single category."""
        name = fake.unique.word().capitalize()
        slug = slugify(name)[:20]
        image_url = fake.image_url(width=400, height=400)
        temp_image = self.download_image(image_url, 'category')

        category = Category(
            name=name,
            parent=parent,
            description=fake.paragraph(),
            slug=slug
        )

        if temp_image:
            with open(temp_image, 'rb') as f:
                category.image.save(os.path.basename(temp_image), File(f))
            os.remove(temp_image)

        category.save()
        return category

    def create_brands(self, count: int) -> List[Brand]:
        """Create brands."""
        brands = []
        for _ in range(count):
            name = fake.unique.company()
            slug = slugify(name)[:20]
            logo_url = fake.image_url(width=300, height=200)
            temp_logo = self.download_image(logo_url, 'brand')

            brand = Brand(
                name=name,
                slug=slug,
                desc=fake.paragraph()
            )

            if temp_logo:
                with open(temp_logo, 'rb') as f:
                    brand.logo.save(os.path.basename(temp_logo), File(f))
                os.remove(temp_logo)

            brand.save()
            brands.append(brand)

        self.stdout.write(self.style.SUCCESS(f'Created {len(brands)} brands'))
        return brands

    def create_products(self, count: int, categories: List[Category], brands: List[Brand]) -> List[Product]:
        """Create products."""
        products = []
        for _ in range(count):
            name = fake.unique.sentence(nb_words=3)[:-1]
            slug = slugify(name)[:20]
            category = random.choice(categories)
            brand = random.choice(brands)
            main_image_url = fake.image_url(width=600, height=600)
            temp_main_image = self.download_image(main_image_url, 'product')

            product = Product(
                name=name,
                category=category,
                brand=brand,
                description='\n'.join(fake.paragraphs(nb=3)),
                price=random.uniform(10, 1000),
                cost=random.uniform(5, 800),
                stock=random.randint(0, 100),
                overall_rating=random.uniform(1, 5),
                trending=random.choice([True, False]),
                slug=slug
            )

            if temp_main_image:
                with open(temp_main_image, 'rb') as f:
                    product.image.save(os.path.basename(temp_main_image), File(f))
                os.remove(temp_main_image)

            product.save()
            self.add_tags_to_product(product)
            self.add_images_to_product(product)
            products.append(product)

        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        return products

    def add_tags_to_product(self, product: Product):
        """Add tags to a product."""
        tags = []
        for _ in range(random.randint(1, 5)):
            tag_name = fake.word()
            tag, _ = Tag.objects.get_or_create(
                key=slugify(tag_name),
                defaults={'name': tag_name.capitalize()}
            )
            tags.append(tag)
        product.tags.set(tags)

    def add_images_to_product(self, product: Product):
        """Add additional images to a product."""
        for _ in range(random.randint(1, 4)):
            image_url = fake.image_url(width=600, height=600)
            temp_image = self.download_image(image_url, 'product_image')

            if temp_image:
                product_image = ProductImage(product=product)
                with open(temp_image, 'rb') as f:
                    product_image.image.save(os.path.basename(temp_image), File(f))
                product_image.save()
                os.remove(temp_image)

    def create_collections(self, count: int, products: List[Product]) -> List[Collection]:
        """Create collections."""
        collections = []
        for _ in range(count):
            name = fake.unique.sentence(nb_words=2)[:-1]
            slug = slugify(name)[:20]

            collection = Collection(
                name=name,
                slug=slug,
                description=fake.paragraph(),
                is_active=random.choice([True, False])
            )
            collection.save()

            products_to_add = random.sample(products, min(len(products), random.randint(3, 10)))
            collection.products.set(products_to_add)
            collections.append(collection)

        self.stdout.write(self.style.SUCCESS(f'Created {len(collections)} collections'))
        return collections

    def create_coupons(self, count: int) -> List[Coupon]:
        """Create coupons."""
        coupons = []
        for _ in range(count):
            code = fake.unique.bothify(text='??##').upper()[:20]
            discount_type = random.choice(['fixed', 'percent'])
            amount = random.uniform(5, 50) if discount_type == 'fixed' else random.uniform(5, 30)
            valid_from = timezone.now()
            valid_to = valid_from + timedelta(days=random.randint(7, 90))

            coupon = Coupon(
                code=code,
                discount_type=discount_type,
                amount=amount,
                active=random.choice([True, False]),
                valid_from=valid_from,
                valid_to=valid_to,
                usage_limit=random.choice([None, random.randint(10, 100)]),
                min_order_value=random.choice([None, random.uniform(20, 100)])
            )
            coupon.save()
            coupons.append(coupon)

        self.stdout.write(self.style.SUCCESS(f'Created {len(coupons)} coupons'))
        return coupons

    def create_reviews(self, count: int, products: List[Product], users: List[User]) -> List[Review]:
        """Create reviews."""
        reviews = []
        for _ in range(count):
            product = random.choice(products)
            user = random.choice(users)

            review = Review(
                product=product,
                user=user,
                content=fake.paragraph(),
                rating=random.randint(1, 5)
            )
            review.save()
            reviews.append(review)

            self.update_product_rating(product)

        self.stdout.write(self.style.SUCCESS(f'Created {len(reviews)} reviews'))
        return reviews

    def update_product_rating(self, product: Product):
        """Update the overall rating of a product."""
        product_reviews = Review.objects.filter(product=product)
        total_rating = sum(review.rating for review in product_reviews)
        product.overall_rating = total_rating / len(product_reviews)
        product.save()
