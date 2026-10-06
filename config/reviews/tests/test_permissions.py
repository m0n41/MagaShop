import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory
from catalog.models import Category, Product
from reviews.models import Review
from reviews.permission import ReviewsListPermission


User = get_user_model()


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
def staff():
    return User.objects.create_user(
        username="staff",
        email="staff@mail.ru",
        password="password123",
        is_staff=True,
    )


@pytest.fixture
def review(user):
    category = Category.objects.create(name="category")

    product = Product.objects.create(
        name="product",
        category=category,
        description="description",
        price=800,
        image="products/test.jpg",
    )

    return Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="review",
    )


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["get", "head", "options"])
def test_permission_safe_methods_allowed(factory, method):
    request = getattr(factory, method)("/reviews/")
    request.user = AnonymousUser()

    permission = ReviewsListPermission()

    assert permission.has_permission(request, None) is True


@pytest.mark.django_db
def test_permission_create_requires_authentication(factory):
    request = factory.post("/reviews/")
    request.user = AnonymousUser()

    permission = ReviewsListPermission()

    assert permission.has_permission(request, None) is False


@pytest.mark.django_db
def test_permission_authenticated_user_can_create(user, factory):
    request = factory.post("/reviews/")
    request.user = user

    permission = ReviewsListPermission()

    assert permission.has_permission(request, None) is True


@pytest.mark.django_db
def test_permission_owner_can_edit_review(user, review, factory):
    request = factory.patch(f"/reviews/{review.id}/")
    request.user = user

    permission = ReviewsListPermission()

    assert permission.has_object_permission(
        request,
        None,
        review,
    ) is True


@pytest.mark.django_db
def test_permission_owner_can_delete_review(user, review, factory):
    request = factory.delete(f"/reviews/{review.id}/")
    request.user = user

    permission = ReviewsListPermission()

    assert permission.has_object_permission(
        request,
        None,
        review,
    ) is True


@pytest.mark.django_db
def test_permission_another_user_cannot_edit_review(
    another_user,
    review,
    factory,
):
    request = factory.patch(f"/reviews/{review.id}/")
    request.user = another_user

    permission = ReviewsListPermission()

    assert permission.has_object_permission(
        request,
        None,
        review,
    ) is False


@pytest.mark.django_db
def test_permission_another_user_cannot_delete_review(
    another_user,
    review,
    factory,
):
    request = factory.delete(f"/reviews/{review.id}/")
    request.user = another_user

    permission = ReviewsListPermission()

    assert permission.has_object_permission(
        request,
        None,
        review,
    ) is False


@pytest.mark.django_db
def test_permission_staff_can_edit_any_review(
    staff,
    review,
    factory,
):
    request = factory.patch(f"/reviews/{review.id}/")
    request.user = staff

    permission = ReviewsListPermission()

    assert permission.has_object_permission(
        request,
        None,
        review,
    ) is True


@pytest.mark.django_db
def test_permission_staff_can_delete_any_review(
    staff,
    review,
    factory,
):
    request = factory.delete(f"/reviews/{review.id}/")
    request.user = staff

    permission = ReviewsListPermission()

    assert permission.has_object_permission(
        request,
        None,
        review,
    ) is True
