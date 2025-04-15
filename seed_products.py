import random
from product.models import Product, Category
from settings.models import Brand
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal

brands = list(Brand.objects.all())
if not brands:
    raise Exception("No brands found. Please create brands first.")

# إنشاء التصنيفات
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

# إنشاء المنتجات
for category in categories:
    names = product_names.get(category.name, [])
    for name in names:
        brand = random.choice(brands)
        price = Decimal(random.randint(3000, 20000))
        cost = price - Decimal(random.randint(500, 1500))

        Product.objects.create(
            name=name,
            category=category,
            brand=brand,
            description=f"{name} by {brand.BRDname} in {category.name}",
            price=price,
            cost=cost,
            stock=random.randint(5, 100),
            overall_rating=round(random.uniform(3.5, 5.0), 1),
            created_at=timezone.now(),
            slug=slugify(name),
        )
