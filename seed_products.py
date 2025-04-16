import random
from product.models import Product, Category
from settings.models import Brand
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal

brands = list(Brand.objects.all())
if not brands:
    # If no brands exist, create 15 default ones
    Brand.objects.create(name="Apple")
    Brand.objects.create(name="Samsung")
    Brand.objects.create(name="Google")
    Brand.objects.create(name="Microsoft")
    Brand.objects.create(name="Lenovo")
    Brand.objects.create(name="Dell")
    Brand.objects.create(name="HP")
    Brand.objects.create(name="Asus")
    Brand.objects.create(name="Acer")
    Brand.objects.create(name="Toshiba")
    Brand.objects.create(name="LG")
    Brand.objects.create(name="Sony")
    Brand.objects.create(name="Panasonic")
    Brand.objects.create(name="Nokia")
    Brand.objects.create(name="Xiaomi")
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
        defaults={"description": desc}
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
        image_url = f"https://picsum.photos/seed/{slugify(name)}/600/400"

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
            image=image_url,
        )

print("Products seeded successfully.")