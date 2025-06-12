from django.core.management.base import BaseCommand
import random
import urllib.request
from decimal import Decimal
from django.utils.text import slugify
from faker import Faker

from product.models import Product, Tag, Category, Review
from features.models import Brand, ProductImage, Collection
from account.models import User
from django.core.files.base import ContentFile

fake = Faker()

IMAGE_URLS = [
    "https://picsum.photos/seed/anystring/600/400",
    "https://loremflickr.com/600/400/product",
    "https://loremflickr.com/600/400/abstract",
    "https://loremflickr.com/600/400/animals",

]

def download_image(url, filename="default.jpg"):
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
            return ContentFile(image_data, name=filename)
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def create_tags(n=10):
    for _ in range(n):
        name = fake.word()
        Tag.objects.get_or_create(key=slugify(name), defaults={"name": name})
    print(f"✅ Created {n} tags.")

def create_brands(n=5):
    for _ in range(n):
        name = fake.company()
        Brand.objects.get_or_create(name=name, defaults={"slug": slugify(name)})

def create_categories(n=5):
    for _ in range(n):
        name = fake.word().capitalize()
        Category.objects.get_or_create(name=name, defaults={"description": fake.text(max_nb_chars=100), "slug": slugify(name)})
    print(f"✅ Created {n} categories.")

def create_dummy_products(n=20):
    tags = list(Tag.objects.all())
    categories = list(Category.objects.all())
    brands = list(Brand.objects.all())
    users = list(User.objects.all())

    for _ in range(n):
        name = fake.sentence(nb_words=3)
        category = random.choice(categories) if categories else None
        brand = random.choice(brands) if brands else None
        price = Decimal(random.uniform(100, 1000)).quantize(Decimal("0.01"))
        cost = (price * Decimal(random.uniform(0.5, 0.9))).quantize(Decimal("0.01"))
        description = fake.paragraph(nb_sentences=3)
        stock = random.randint(0, 100)
        discount = random.randint(0, 30)

        product = Product.objects.create(
            name=name,
            category=category,
            brand=brand,
            description=description,
            price=price,
            cost=cost,
            stock=stock,
            trending=random.choice([True, False]),
            slug=slugify(name)
        )

        image_url = random.choice(IMAGE_URLS)
        main_image = download_image(image_url, f"{slugify(name)}.jpg")
        if main_image:
            product.image.save(f"{slugify(name)}.jpg", main_image)

        for i in range(random.randint(1, 3)):
            img_url = random.choice(IMAGE_URLS)
            img_file = download_image(img_url, f"{slugify(name)}-{i}.jpg")
            if img_file:
                ProductImage.objects.create(product=product, image=img_file)

        product.tags.set(random.sample(tags, min(len(tags), random.randint(1, 3))))

        for _ in range(random.randint(0, 5)):
            if users:
                Review.objects.create(
                    product=product,
                    user=random.choice(users),
                    content=fake.text(max_nb_chars=200),
                    rating=random.randint(1, 5)
                )

        product.update_overall_rating()

    print(f"✅ Created {n} dummy products.")

def create_collections(n=5):
    products = list(Product.objects.all())
    for _ in range(n):
        name = fake.word().capitalize()
        collection = Collection.objects.create(
            name=name,
            slug=slugify(name),
            description=fake.text(max_nb_chars=100),
            is_active=random.choice([True, False])
        )
        # Add random products to the collection
        collection.products.set(random.sample(products, min(len(products), random.randint(1, 5))))
        collection.save()

    print(f"✅ Created {n} collections.")



class Command(BaseCommand):
    help = "Generate dummy products, tags, brands, and categories."

    def handle(self, *args, **kwargs):
        create_tags(10)
        create_brands(5)
        create_categories(5)
        create_dummy_products(20)
        create_collections(5)  
