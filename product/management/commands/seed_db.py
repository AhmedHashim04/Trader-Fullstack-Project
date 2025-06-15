# app/management/commands/seed_db.py
import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from features.models import Brand, ProductImage, Collection
from product.models import Tag, Product, Category, Review

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed database with fake but realistic data'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Delete all seeded data')

    def handle(self, *args, **kwargs):
        if kwargs['delete']:
            return self._delete_data()

        self.stdout.write(self.style.SUCCESS("Seeding started..."))
        self._create_categories()
        self._create_brands()
        self._create_tags()
        self._create_products(n=100)
        self._create_reviews()
        self._create_collections()
        self.stdout.write(self.style.SUCCESS("✅ Seeding completed!"))


    def get_unique_slug(self,model, name):
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while model.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    def _create_categories(self):
        self.categories = []
        for _ in range(10):
            name = fake.word().capitalize()
            category = Category(name=name, description=fake.text(max_nb_chars=200))
            category.slug = self.get_unique_slug(Category, name),
            self.categories.append(category)
        Category.objects.bulk_create(self.categories)

    def _create_brands(self):
        self.brands = []
        for _ in range(10):
            name = fake.company()
            brand = Brand(name=name, desc=fake.text(100))
            brand.slug = self.get_unique_slug(Brand, name),
            self.brands.append(brand)
        Brand.objects.bulk_create(self.brands)

    def _create_tags(self):
        self.tags = []
        existing_keys = set(Tag.objects.values_list('key', flat=True))
        for _ in range(20):
            while True:
                name = fake.word()
                key = name.lower()
                if key not in existing_keys:
                    existing_keys.add(key)
                    break
            tag = Tag(key=key, name=name.capitalize())
            self.tags.append(tag)
        Tag.objects.bulk_create(self.tags)

    def _create_products(self, n=100):
        self.products = []
        for _ in range(n):
            name = fake.unique.word().capitalize()
            product = Product(
                name=name,
                description=fake.text(300),
                price=round(random.uniform(50, 5000), 2),
                cost=round(random.uniform(30, 4000), 2),
                category=random.choice(self.categories),
                brand=random.choice(self.brands),
                stock=random.randint(0, 100),
                discount=random.uniform(0, 50),
                trending=random.choice([True, False]),
            )
            product.slug =self.get_unique_slug(Product, name),
            self.products.append(product)
        Product.objects.bulk_create(self.products)

        # ManyToMany relationships need saving after insert
        for product in Product.objects.all():
            product.tags.set(random.sample(list(Tag.objects.all()), k=random.randint(1, 4)))

    def _create_reviews(self):
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING("⚠️ No users found to create reviews."))
            return

        reviews = []
        for product in Product.objects.all():
            chosen_users = random.sample(users, min(len(users), random.randint(1, 5)))
            for user in chosen_users:
                if not Review.objects.filter(product=product, user=user).exists():
                    review = Review(
                        product=product,
                        user=user,
                        rating=random.randint(1, 5),
                        content=fake.sentence(),
                    )
                    reviews.append(review)
        Review.objects.bulk_create(reviews)

        # Update ratings
        for product in Product.objects.all():
            product.update_rating()

    def _create_collections(self):
        for _ in range(5):
            name = fake.word().capitalize() + " Collection"
            collection = Collection.objects.create(
                name=name,
                slug=slugify(name),
                description=fake.text(150),
            )
            collection.products.set(random.sample(list(Product.objects.all()), k=random.randint(5, 20)))

    def _delete_data(self):
        Review.objects.all().delete()
        Product.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Collection.objects.all().delete()
        ProductImage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("🗑️ All seeded data deleted successfully."))



