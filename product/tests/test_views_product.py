import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from product.models import Product, Category, Tag, Review
from features.models import Brand
from account.models import Profile


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")

@pytest.fixture
def profile(db, user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

@pytest.fixture
def category():
    return Category.objects.create(name="Phones", description="Phones cat")

@pytest.fixture
def brand():
    return Brand.objects.create(name="Apple", slug="apple")

@pytest.fixture
def product(category, brand):
    return Product.objects.create(
        name="iPhone 15", 
        category=category, 
        brand=brand,
        price=1000, 
        cost=800,
        description="Smartphone"
    )

@pytest.fixture
def create_products(category, brand):
    return [
        Product.objects.create(
            name=f"Product {i}",
            category=category,
            brand=brand,
            price=100 + i,
            cost=80 + i,
            description="Sample"
        )
        for i in range(3)
    ]

@pytest.mark.django_db
def test_product_list_view(client, create_products):
    url = reverse("product:products_list")
    response = client.get(url)
    assert response.status_code == 200
    assert b"products" in response.content


@pytest.mark.django_db
def test_product_filter_by_category(client, category, brand):
    product = Product.objects.create(
        name="iPhone",
        category=category,
        brand=brand,
        price=1000,
        cost=700,
        description="..."
    )
    url = reverse("product:products_list")
    response = client.get(url, {"category": category.slug})
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_product_detail_view(client, user, product):
    client.force_login(user)
    url = reverse("product:product_detail", kwargs={"slug": product.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_review_submission(client, user, product):
    client.force_login(user)
    url = reverse("product:product_detail", kwargs={"slug": product.slug})
    data = {"content": "Great!", "rating": 5}
    response = client.post(url, data, follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Thank you for your review!" in messages
    assert Review.objects.filter(product=product, user=user).exists()


@pytest.mark.django_db
def test_duplicate_review_warning(client, user, product):
    Review.objects.create(product=product, user=user, rating=5, content="Great!")
    client.force_login(user)
    url = reverse("product:product_detail", kwargs={"slug": product.slug})
    response = client.post(url, {"content": "Again", "rating": 4}, follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "already reviewed" in messages[0]


@pytest.mark.django_db
def test_compare_products_view(client, user, create_products):
    client.force_login(user)
    p1, p2 = create_products[:2]
    url = reverse("product:compare_products") + f"?product_slug={p1.slug}&product_slug={p2.slug}"
    response = client.get(url)
    assert response.status_code == 200
    assert p1.name in response.content.decode()
    assert p2.name in response.content.decode()


@pytest.mark.django_db
def test_compare_products_less_than_two_raises_404(client, user, product):
    client.force_login(user)
    url = reverse("product:compare_products") + f"?product_slug={product.slug}"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_wishlist_add_remove(client, user, profile, product):
    client.force_login(user)
    url = reverse("product:add_remove_wishlist", kwargs={"slug": product.slug})
    response = client.get(url, follow=True)
    profile.refresh_from_db()
    assert product in profile.wishlist.all()

    # remove again
    response = client.get(url, follow=True)
    profile.refresh_from_db()
    assert product not in profile.wishlist.all()


@pytest.mark.django_db
def test_clear_wishlist(client, user, profile, product):
    profile.wishlist.add(product)
    client.force_login(user)
    url = reverse("product:clear_wishlist")
    response = client.get(url, follow=True)
    profile.refresh_from_db()
    assert profile.wishlist.count() == 0


@pytest.mark.django_db
def test_user_see_product(client, user, profile, product):
    client.force_login(user)
    url = reverse("product:user_see_product", kwargs={"slug": product.slug})
    response = client.get(url)
    assert response.status_code == 302  # redirect to product detail
    assert profile in product.viewed_by.all()
