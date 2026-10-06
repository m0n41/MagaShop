import pytest
from django.db import IntegrityError
from wishlist.models import Wishlist
from users.models import User
from catalog.models import Category, Product


@pytest.mark.django_db
def test_wishlist_creation():
    user = User.objects.create_user(
        username="user1",
        email="user1@mail.ru",
        password="password123",
    )

    category = Category.objects.create(
        name="Телефоны",
        slug="phones",
    )

    product = Product.objects.create(
        name="iPhone",
        slug="iphone",
        category=category,
        brand="Apple",
        description="Smartphone",
        price=100000,
        stock=10,
        is_available=True,
    )

    wishlist = Wishlist.objects.create(
        user=user,
        product=product,
    )

    assert wishlist.user == user
    assert wishlist.product == product


@pytest.mark.django_db
def test_same_user_cannot_add_same_product_twice():
    user = User.objects.create_user(
        username="user1",
        email="user1@mail.ru",
        password="password123",
    )

    category = Category.objects.create(
        name="Телефоны",
        slug="phones",
    )

    product = Product.objects.create(
        name="iPhone",
        slug="iphone",
        category=category,
        brand="Apple",
        description="Smartphone",
        price=100000,
        stock=10,
        is_available=True,
    )

    Wishlist.objects.create(
        user=user,
        product=product,
    )

    with pytest.raises(IntegrityError):
        Wishlist.objects.create(
            user=user,
            product=product,
        )


@pytest.mark.django_db
def test_different_users_can_add_same_product():
    user1 = User.objects.create_user(
        username="user1",
        email="user1@mail.ru",
        password="password123",
    )

    user2 = User.objects.create_user(
        username="user2",
        email="user2@mail.ru",
        password="password123",
    )

    category = Category.objects.create(
        name="Телефоны",
        slug="phones",
    )

    product = Product.objects.create(
        name="iPhone",
        slug="iphone",
        category=category,
        brand="Apple",
        description="Smartphone",
        price=100000,
        stock=10,
        is_available=True,
    )

    Wishlist.objects.create(
        user=user1,
        product=product,
    )

    Wishlist.objects.create(
        user=user2,
        product=product,
    )

    assert Wishlist.objects.filter(product=product).count() == 2