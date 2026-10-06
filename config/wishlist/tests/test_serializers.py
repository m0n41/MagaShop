import pytest

from rest_framework.test import APIRequestFactory

from wishlist.models import Wishlist
from wishlist.serializer import WishlistSerializer
from users.models import User
from catalog.models import Category, Product


@pytest.fixture
def user():
    return User.objects.create_user(
        username="user1",
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


@pytest.mark.django_db
def test_wishlist_serializer_valid(user, product):
    factory = APIRequestFactory()
    request = factory.post("/wishlist/")
    request.user = user

    serializer = WishlistSerializer(
        data={"product": product.id},
        context={"request": request},
    )

    assert serializer.is_valid()
    assert serializer.validated_data["product"] == product


@pytest.mark.django_db
def test_wishlist_serializer_rejects_duplicate(user, product):
    Wishlist.objects.create(
        user=user,
        product=product,
    )

    factory = APIRequestFactory()
    request = factory.post("/wishlist/")
    request.user = user

    serializer = WishlistSerializer(
        data={"product": product.id},
        context={"request": request},
    )

    assert not serializer.is_valid()
    assert "Вы уже добавили в избранное." in str(serializer.errors)


@pytest.mark.django_db
def test_wishlist_serializer_rejects_nonexistent_product(user):
    factory = APIRequestFactory()
    request = factory.post("/wishlist/")
    request.user = user

    serializer = WishlistSerializer(
        data={"product": 999999},
        context={"request": request},
    )

    assert not serializer.is_valid()
    assert "product" in serializer.errors