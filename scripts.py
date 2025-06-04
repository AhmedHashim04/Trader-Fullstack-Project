import os
import random
import django
from django.utils.translation import gettext as _

# Ensure Django is set up
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from settings.models import Brand
from product.models import Product, Category, Tag, Review
from account.models import User


def generate_brands(num_brands):
    """Generate random brands."""
    if num_brands <= 0:
        print("Number of brands must be greater than 0.")
        return

    brands = [
        Brand(name=f"Brand {i + 1}", desc=f"Description for Brand {i + 1}")
        for i in range(num_brands)
    ]
    Brand.objects.bulk_create(brands)
    print(f"{num_brands} brands created successfully.")


def generate_categories(num_categories):
    """Generate random categories."""
    if num_categories <= 0:
        print("Number of categories must be greater than 0.")
        return

    categories = [
        Category(name=f"Category {i + 1}", description=f"Description for Category {i + 1}")
        for i in range(num_categories)
    ]
    Category.objects.bulk_create(categories)
    print(f"{num_categories} categories created successfully.")


def generate_users(num_users):
    """Generate random users."""
    if num_users <= 0:
        print("Number of users must be greater than 0.")
        return

    for i in range(num_users):
        username = f"user{i + 1}"
        email = f"user{i + 1}@example.com"
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                email=email,
                password="password123"
            )
    print(f"{num_users} users created successfully.")


def add_reviews(num_reviews):
    """Add random reviews to products."""
    if num_reviews <= 0:
        print("Number of reviews must be greater than 0.")
        return

    users = list(User.objects.all())
    products = list(Product.objects.all())

    if not users or not products:
        print("Please create users and products first.")
        return

    reviews = [
        Review(
            product=random.choice(products),
            user=random.choice(users),
            rating=random.randint(1, 5),
            comment=f"This is a review for {random.choice(products).name} by {random.choice(users).username}."
        )
        for _ in range(num_reviews)
    ]
    Review.objects.bulk_create(reviews)
    print(f"{num_reviews} reviews added successfully.")


def generate_products(num_products):
    """Generate random products."""
    if num_products <= 0:
        print("Number of products must be greater than 0.")
        return

    brands = list(Brand.objects.all())
    categories = list(Category.objects.all())
    tags = list(Tag.objects.all())

    if not brands or not categories:
        print("Please create brands and categories first.")
        return

    products = []
    for i in range(num_products):
        product_name = f"Product {i + 1}"
        product = Product(
            name=product_name,
            description=f"Description for {product_name}",
            price=round(random.uniform(10, 100), 2),
            stock=random.randint(1, 50),
            brand=random.choice(brands),
            category=random.choice(categories),
            trending=random.choice([True, False]),
            image=f"https://picsum.photos/500/500?random={i}"
        )
        products.append(product)

    created_products = Product.objects.bulk_create(products)

    # Assign random tags to products
    for product in created_products:
        product.tags.set(random.sample(tags, min(len(tags), random.randint(1, 3))))

    print(f"{num_products} products created successfully.")


def clean_data():
    """Remove all data from the database, except superusers."""
    for model in [Product, Category, Brand, Tag, Review]:
        model.objects.all().delete()

    User.objects.exclude(is_superuser=True).delete()
    print("All data has been removed successfully, except superusers.")


def add_tags():
    """Add predefined tags into the database."""
    tags = [
        ("new", _("New")),
        ("best", _("Best")),
        ("sale", _("Sale")),
        ("summer", _("Summer")),
        ("winter", _("Winter")),
        ("spring", _("Spring")),
        ("autumn", _("Autumn")),
        ("limited", _("Limited")),
        ("recommended", _("Recommended")),
        ("gift", _("Gift")),
        ("popular", _("Popular")),
        ("top", _("Top")),
        ("exclusive", _("Exclusive")),
        ("special", _("Special")),
        ("new_arrivals", _("New Arrivals")),
        ("best_sellers", _("Best Sellers")),
        ("on_sale", _("On Sale")),
        ("summer_collection", _("Summer Collection")),
        ("winter_collection", _("Winter Collection")),
        ("spring_collection", _("Spring Collection")),
        ("autumn_collection", _("Autumn Collection")),
        ("limited_collection", _("Limited Collection")),
        ("recommended_collection", _("Recommended Collection")),
        ("gift_collection", _("Gift Collection")),
        ("popular_collection", _("Popular Collection")),
        ("top_collection", _("Top Collection")),
        ("exclusive_collection", _("Exclusive Collection")),
        ("special_collection", _("Special Collection")),
        ("new_arrivals_collection", _("New Arrivals Collection")),
        ("best_sellers_collection", _("Best Sellers Collection")),
        ("on_sale_collection", _("On Sale Collection")),
    ]
    for key, name in tags:
        Tag.objects.get_or_create(key=key, name=name)
    print("Tags have been added successfully.")


def main():
    print("Welcome to the Data Generator Program!")
    while True:
        print("\nChoose an option:")
        print("1. Generate Brands")
        print("2. Generate Categories")
        print("3. Generate Users")
        print("4. Generate Products")
        print("5. Add Reviews")
        print("6. Clean Data")
        print("7. Add Tags")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            num_brands = int(input("Enter the number of brands to generate: "))
            generate_brands(num_brands)
        elif choice == "2":
            num_categories = int(input("Enter the number of categories to generate: "))
            generate_categories(num_categories)
        elif choice == "3":
            num_users = int(input("Enter the number of users to generate: "))
            generate_users(num_users)
        elif choice == "4":
            num_products = int(input("Enter the number of products to generate: "))
            generate_products(num_products)
        elif choice == "5":
            num_reviews = int(input("Enter the number of reviews to add: "))
            add_reviews(num_reviews)
        elif choice == "6":
            clean_data()
        elif choice == "7":
            add_tags()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
