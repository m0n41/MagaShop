import pytest
from rest_framework.test import APIClient
from wishlist.models import Wishlist
from users.models import User
from catalog.models import Category, Product


@pytest.fixture
def user():
    return User.objects.create_user(
        username="user1",
        email="user1@mail.ru",
        password="password123",
    )


@pytest.fixture
def another_user():
    return User.objects.create_user(
        username="user2",
        email="user2@mail.ru",
        password="password123",
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Телефоны",
        slug="phones",
    )


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="iPhone",
        slug="iphone",
        category=category,
        brand="Apple",
        description="Smartphone",
        price=100000,
        stock=10,
        is_available=True,
    )


@pytest.fixture
def another_product(category):
    return Product.objects.create(
        name="Samsung",
        slug="samsung",
        category=category,
        brand="Samsung",
        description="Smartphone",
        price=80000,
        stock=10,
        is_available=True,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_anonymous_cannot_get_wishlist(client):
    response = client.get("/api/v1/wishlist/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_anonymous_cannot_add_wishlist(client, product):
    response = client.post(
        "/api/v1/wishlist/",
        {"product": product.id},
        format="json",
    )

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_authenticated_user_can_get_own_wishlist(
    client,
    user,
    product,
):
    client.force_authenticate(user=user)

    Wishlist.objects.create(
        user=user,
        product=product,
    )

    response = client.get("/api/v1/wishlist/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["product"] == product.id


@pytest.mark.django_db
def test_user_sees_only_own_wishlist(
    client,
    user,
    another_user,
    product,
    another_product,
):
    client.force_authenticate(user=user)

    Wishlist.objects.create(
        user=user,
        product=product,
    )

    Wishlist.objects.create(
        user=another_user,
        product=another_product,
    )

    response = client.get("/api/v1/wishlist/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["product"] == product.id


@pytest.mark.django_db
def test_authenticated_user_can_add_product(
    client,
    user,
    product,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/wishlist/",
        {"product": product.id},
        format="json",
    )

    assert response.status_code == 201

    wishlist = Wishlist.objects.get(
        user=user,
        product=product,
    )

    assert wishlist.user == user
    assert wishlist.product == product


@pytest.mark.django_db
def test_user_cannot_spoof_owner(
    client,
    user,
    another_user,
    product,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/wishlist/",
        {
            "product": product.id,
            "user": another_user.id,
        },
        format="json",
    )

    assert response.status_code == 201

    wishlist = Wishlist.objects.get(
        product=product,
    )

    assert wishlist.user == user


@pytest.mark.django_db
def test_duplicate_wishlist_returns_400(
    client,
    user,
    product,
):
    client.force_authenticate(user=user)

    Wishlist.objects.create(
        user=user,
        product=product,
    )

    response = client.post(
        "/api/v1/wishlist/",
        {"product": product.id},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_nonexistent_product_returns_400(
    client,
    user,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/wishlist/",
        {"product": 999999},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_can_delete_own_wishlist(
    client,
    user,
    product,
):
    client.force_authenticate(user=user)

    wishlist = Wishlist.objects.create(
        user=user,
        product=product,
    )

    response = client.delete(
        f"/api/v1/wishlist/{wishlist.id}/"
    )

    assert response.status_code == 204
    assert not Wishlist.objects.filter(
        id=wishlist.id
    ).exists()


@pytest.mark.django_db
def test_user_cannot_delete_foreign_wishlist(
    client,
    user,
    another_user,
    product,
):
    client.force_authenticate(user=user)

    wishlist = Wishlist.objects.create(
        user=another_user,
        product=product,
    )

    response = client.delete(
        f"/api/v1/wishlist/{wishlist.id}/"
    )

    assert response.status_code == 404
    assert Wishlist.objects.filter(
        id=wishlist.id
    ).exists()


@pytest.mark.django_db
def test_delete_nonexistent_wishlist_returns_404(
    client,
    user,
):
    client.force_authenticate(user=user)

    response = client.delete(
        "/api/v1/wishlist/999999/"
    )

    assert response.status_code == 404