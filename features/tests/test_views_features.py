import pytest
from django.urls import reverse
from features.models import Collection, Brand
from product.models import Product, Category, Tag

@pytest.fixture
def brand():
    return Brand.objects.create(name="Apple", slug="apple")

@pytest.fixture
def category():
    return Category.objects.create(name="Smartphones", slug="smartphones")

@pytest.fixture
def tag():
    return Tag.objects.create(name="New")

@pytest.fixture
def collection():
    return Collection.objects.create(name="Best Deals", slug="best-deals")

@pytest.fixture
def products(collection, brand, category, tag):
    p1 = Product.objects.create(name="iPhone", slug="iphone", price=1000, cost=800, brand=brand, category=category)
    p2 = Product.objects.create(name="Galaxy", slug="galaxy", price=800, cost=600, brand=brand, category=category)
    p1.tags.add(tag)
    p2.tags.add(tag)
    collection.products.add(p1, p2)
    return [p1, p2]

@pytest.mark.django_db
def test_collection_detail_view_shows_products(client, collection, products):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url)
    assert response.status_code == 200
    for product in products:
        assert product.name in response.content.decode()

@pytest.mark.django_db
def test_collection_search_filter(client, collection, products):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url, {"search": "iPhone"})
    assert b"iPhone" in response.content
    assert b"Galaxy" not in response.content

@pytest.mark.django_db
def test_filter_by_brand(client, collection, products, brand):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url, {"brand": brand.slug})
    assert b"iPhone" in response.content

@pytest.mark.django_db
def test_filter_by_category(client, collection, products, category):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url, {"category": category.slug})
    assert b"iPhone" in response.content

@pytest.mark.django_db
def test_filter_by_tag(client, collection, products, tag):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url, {"tag": tag.name})
    assert b"iPhone" in response.content

@pytest.mark.django_db
def test_price_range_filter(client, collection, products):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url, {"min_price": "900"})
    assert b"iPhone" in response.content
    assert b"Galaxy" not in response.content

@pytest.mark.django_db
def test_sorting_by_price_desc(client, collection, products):
    url = reverse("features:collection_detail", kwargs={"slug": collection.slug})
    response = client.get(url, {"sort_by": "price_desc"})
    content = response.content.decode()
    assert content.index("iPhone") < content.index("Galaxy")

