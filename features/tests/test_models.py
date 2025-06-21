import pytest
from django.utils.text import slugify
from product.models import Product
from features.models import ProductImage, Brand, Collection

@pytest.mark.django_db
def test_product_image_str_representation():
    product = Product.objects.create(name="iPhone", slug="iphone", cost=500, price=700)
    image = ProductImage.objects.create(product=product, image="product_images/iphone.png")
    assert str(image) == f"Image for {product.name}"


@pytest.mark.django_db
def test_brand_str_and_slug_generation():
    brand = Brand.objects.create(name="Apple")
    assert str(brand) == "Apple"
    assert brand.slug == slugify("Apple")


@pytest.mark.django_db
def test_brand_slug_not_overwritten_if_exists():
    brand = Brand.objects.create(name="Samsung", slug="custom-slug")
    assert brand.slug == "custom-slug"


@pytest.mark.django_db
def test_collection_str_representation():
    collection = Collection.objects.create(name="Summer Sale", slug="summer-sale")
    assert str(collection) == "Summer Sale"


@pytest.mark.django_db
def test_collection_products_relationship():
    product1 = Product.objects.create(name="iPhone", slug="iphone", cost=500, price=700)
    product2 = Product.objects.create(name="Galaxy", slug="galaxy", cost=400, price=600)
    collection = Collection.objects.create(name="Hot Deals", slug="hot-deals")
    collection.products.set([product1, product2])
    assert collection.products.count() == 2
    assert product1 in collection.products.all()
