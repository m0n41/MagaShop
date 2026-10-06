import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory
from wishlist.models import Wishlist
from wishlist.permission import WishlistPermission
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
def product():
    category = Category.objects.create(
        name="Телефоны",
        slug="phones",
    )

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
def test_anonymous_user_has_no_permission():
    factory = APIRequestFactory()
    request = factory.get("/wishlist/")
    request.user = AnonymousUser()

    permission = WishlistPermission()

    assert permission.has_permission(request, None) is False


@pytest.mark.django_db
def test_authenticated_user_has_permission(user):
    factory = APIRequestFactory()
    request = factory.get("/wishlist/")
    request.user = user

    permission = WishlistPermission()

    assert permission.has_permission(request, None) is True


@pytest.mark.django_db
def test_owner_can_access_own_wishlist(user, product):
    wishlist = Wishlist.objects.create(
        user=user,
        product=product,
    )

    factory = APIRequestFactory()
    request = factory.delete("/wishlist/")
    request.user = user

    permission = WishlistPermission()

    assert permission.has_object_permission(
        request,
        None,
        wishlist,
    ) is True


@pytest.mark.django_db
def test_user_cannot_access_foreign_wishlist(
    user,
    another_user,
    product,
):
    wishlist = Wishlist.objects.create(
        user=another_user,
        product=product,
    )

    factory = APIRequestFactory()
    request = factory.delete("/wishlist/")
    request.user = user

    permission = WishlistPermission()

    assert permission.has_object_permission(
        request,
        None,
        wishlist,
    ) is False