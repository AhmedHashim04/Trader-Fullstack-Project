import pytest
from django.utils.text import slugify
from django.urls import reverse
from product.models import Product, Category, Tag, Review
from features.models import Brand
from django.contrib.auth.models import User
from decimal import Decimal


@pytest.mark.django_db
def test_tag_str():
    tag = Tag.objects.create(name="New", color="#fff", bg_color="#000")
    assert str(tag) == "New"


@pytest.mark.django_db
def test_category_slug_generation():
    cat = Category.objects.create(name="Phones", description="desc")
    assert cat.slug == slugify("Phones")



@pytest.mark.django_db
def test_product_slug_generation():
    brand = Brand.objects.create(name="Apple")
    category = Category.objects.create(name="Mobiles", description="desc")
    product = Product.objects.create(name="iPhone 14", brand=brand, category=category, price=1000, cost=800, description="...")
    assert product.slug == slugify("iPhone 14")


@pytest.mark.django_db
def test_product_str_and_url():
    brand = Brand.objects.create(name="Apple")
    category = Category.objects.create(name="Mobiles", description="desc")
    product = Product.objects.create(name="Galaxy S21", brand=brand, category=category, price=900, cost=700, description="...")
    assert str(product) == "Galaxy S21"
    assert product.get_absolute_url() == reverse("product:product_detail", kwargs={"slug": product.slug})


@pytest.mark.django_db
def test_product_properties():
    brand = Brand.objects.create(name="TestBrand")
    category = Category.objects.create(name="TestCategory", description="desc")
    product = Product.objects.create(name="TestPhone", brand=brand, category=category, price=1000, cost=800, stock=10, discount=10, description="...")
    assert product.price_after_discount == Decimal("900.0")
    assert product.is_in_stock is True
    assert product.has_discount is True
    assert product.is_on_sale is True


@pytest.mark.django_db
def test_review_creation_and_rating_update():
    user = User.objects.create_user(username="john", password="pass")
    brand = Brand.objects.create(name="TestBrand")
    category = Category.objects.create(name="TestCategory", description="desc")
    product = Product.objects.create(name="TestProduct", brand=brand, category=category, price=1000, cost=800, description="...")
    assert product.overall_rating == 0.0

    Review.objects.create(product=product, user=user, rating=4, content="Good")
    product.refresh_from_db()
    assert product.overall_rating == 4.0


@pytest.mark.django_db
def test_review_delete_updates_rating():
    user = User.objects.create_user(username="john", password="pass")
    brand = Brand.objects.create(name="TestBrand")
    category = Category.objects.create(name="TestCategory", description="desc")
    product = Product.objects.create(name="AnotherProduct", brand=brand, category=category, price=500, cost=300, description="...")
    review = Review.objects.create(product=product, user=user, rating=5, content="Excellent")
    product.refresh_from_db()
    assert product.overall_rating == 5.0

    review.delete()
    product.refresh_from_db()
    assert product.overall_rating == 0.0


@pytest.mark.django_db
def test_unique_review_constraint():
    user = User.objects.create_user(username="jane", password="pass")
    brand = Brand.objects.create(name="TestBrand")
    category = Category.objects.create(name="TestCategory", description="desc")
    product = Product.objects.create(name="SomeProduct", brand=brand, category=category, price=200, cost=100, description="...")
    Review.objects.create(product=product, user=user, rating=3, content="Ok")
    with pytest.raises(Exception):
        Review.objects.create(product=product, user=user, rating=4, content="Updated")
