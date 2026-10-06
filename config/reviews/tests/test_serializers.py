import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from catalog.models import Category, Product
from reviews.models import Review
from reviews.serializers import ReviewSerializer


User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="testuser@mail.ru",
        password="password123",
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="testcategory")

    return Product.objects.create(
        name="testproduct",
        category=category,
        description="testproductdescription",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )


@pytest.fixture
def request_factory():
    return APIRequestFactory()


@pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
@pytest.mark.django_db
def test_serializer_valid_rating(
    rating,
    user,
    product,
    request_factory,
):
    request = request_factory.post("/reviews/")
    request.user = user

    serializer = ReviewSerializer(
        data={
            "product": product.id,
            "rating": rating,
            "text": "test review",
        },
        context={"request": request},
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.parametrize("rating", [0, 6, -1])
@pytest.mark.django_db
def test_serializer_invalid_rating(
    rating,
    user,
    product,
    request_factory,
):
    request = request_factory.post("/reviews/")
    request.user = user

    serializer = ReviewSerializer(
        data={
            "product": product.id,
            "rating": rating,
            "text": "test review",
        },
        context={"request": request},
    )

    assert serializer.is_valid() is False
    assert "rating" in serializer.errors


@pytest.mark.django_db
def test_serializer_duplicate_review(
    user,
    product,
    request_factory,
):
    Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="old review",
    )

    request = request_factory.post("/reviews/")
    request.user = user

    serializer = ReviewSerializer(
        data={
            "product": product.id,
            "rating": 4,
            "text": "new review",
        },
        context={"request": request},
    )

    assert serializer.is_valid() is False

    assert "Вы уже оставляли отзыв на этот товар." in str(
        serializer.errors
    )


@pytest.mark.django_db
def test_serializer_update_own_review(
    user,
    product,
    request_factory,
):
    review = Review.objects.create(
        product=product,
        user=user,
        rating=3,
        text="old review",
    )

    request = request_factory.patch(f"/reviews/{review.id}/")
    request.user = user

    serializer = ReviewSerializer(
        review,
        data={
            "product": product.id,
            "rating": 5,
            "text": "updated review",
        },
        context={"request": request},
    )

    assert serializer.is_valid(), serializer.errors

    updated_review = serializer.save()

    assert updated_review.rating == 5
    assert updated_review.text == "updated review"


@pytest.mark.django_db
def test_serializer_user_cannot_be_changed(
    user,
    product,
    request_factory,
):
    another_user = User.objects.create_user(
        username="anotheruser",
        password="password123",
    )

    request = request_factory.post("/reviews/")
    request.user = user

    serializer = ReviewSerializer(
        data={
            "product": product.id,
            "rating": 5,
            "text": "test review",
            "user": another_user.id,
        },
        context={"request": request},
    )

    assert serializer.is_valid(), serializer.errors

    assert "user" not in serializer.validated_data