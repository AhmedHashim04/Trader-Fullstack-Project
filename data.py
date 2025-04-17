from product.models import Category, Product
from settings.models import Brand
from django.utils.text import slugify
import random

# بيانات تجريبية
brand_names = ["Apple", "Samsung", "Nike", "Adidas", "Sony"]
category_data = [
    {"name": "Electronics", "description": "Devices and gadgets"},
    {"name": "Clothing", "description": "Fashion and apparel"},
    {"name": "Shoes", "description": "Footwear for all"},
    {"name": "Home Appliances", "description": "Home & Kitchen utilities"},
    {"name": "Accessories", "description": "Extras to complete your style"},
]

product_data = [
    {"name": "iPhone 14 Pro", "price": 999.99, "cost": 750.00, "stock": 25},
    {"name": "Galaxy S23", "price": 899.99, "cost": 670.00, "stock": 20},
    {"name": "Air Jordan 1", "price": 199.99, "cost": 120.00, "stock": 40},
    {"name": "Sony Headphones", "price": 149.99, "cost": 90.00, "stock": 60},
    {"name": "Microwave Oven", "price": 250.00, "cost": 180.00, "stock": 15},
    {"name": "Adidas T-Shirt", "price": 39.99, "cost": 20.00, "stock": 100},
    {"name": "Apple Watch", "price": 399.99, "cost": 290.00, "stock": 30},
]

# 1. إنشاء البراندات
brands = []
for name in brand_names:
    brand, _ = Brand.objects.get_or_create(name=name)
    brands.append(brand)

# 2. إنشاء التصنيفات
categories = []
for cat in category_data:
    category, _ = Category.objects.get_or_create(
        name=cat["name"],
        defaults={"description": cat["description"], "slug": slugify(cat["name"])}
    )
    categories.append(category)

# 3. إنشاء المنتجات
for data in product_data:
    product_name = data["name"]
    slug = slugify(product_name)
    price = data["price"]
    cost = data["cost"]
    stock = data["stock"]
    description = f"Awesome product: {product_name}"
    image_url = f"https://via.placeholder.com/300x300.png?text={slug.replace('-', '+')}"

    Product.objects.get_or_create(
        name=product_name,
        defaults={
            "slug": slug,
            "description": description,
            "price": price,
            "cost": cost,
            "category": random.choice(categories),
            "brand": random.choice(brands),
            "image": image_url,
            "stock": stock,
        }
    )

print("✅ تمت إضافة البيانات التجريبية بنجاح!")
