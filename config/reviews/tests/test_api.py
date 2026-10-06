import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from catalog.models import Category, Product
from reviews.models import Review


User = get_user_model()

URL = "/api/v1/reviews/"


@pytest.fixture
def api_client():
    return APIClient()


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
def product():
    category = Category.objects.create(name="category")

    return Product.objects.create(
        name="product",
        category=category,
        description="description",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )


@pytest.fixture
def second_product():
    category = Category.objects.create(name="category2")

    return Product.objects.create(
        name="product2",
        category=category,
        description="description2",
        price=900,
        image="products/test2.jpg",
    )


@pytest.fixture
def review(user, product):
    return Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="test review",
    )


@pytest.mark.django_db
def test_reviews_list_returns_200(api_client, review):
    response = api_client.get(URL)

    assert response.status_code == 200
    assert response.json()


@pytest.mark.django_db
def test_guest_sees_only_active_reviews(
    api_client,
    user,
    another_user,
    product,
):
    active_review = Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="active",
        is_active=True,
    )

    inactive_review = Review.objects.create(
        product=product,
        user=another_user,
        rating=3,
        text="inactive",
        is_active=False,
    )

    response = api_client.get(URL)

    assert response.status_code == 200

    ids = [item["id"] for item in response.json()["results"]]

    assert active_review.id in ids
    assert inactive_review.id not in ids


@pytest.mark.django_db
def test_staff_sees_inactive_reviews(
    api_client,
    staff,
    user,
    another_user,
    product,
):
    active_review = Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="active",
        is_active=True,
    )

    inactive_review = Review.objects.create(
        product=product,
        user=another_user,
        rating=3,
        text="inactive",
        is_active=False,
    )

    api_client.force_authenticate(user=staff)

    response = api_client.get(URL)

    assert response.status_code == 200

    ids = [item["id"] for item in response.json()["results"]]

    assert active_review.id in ids
    assert inactive_review.id in ids


@pytest.mark.django_db
def test_filter_reviews_by_product(
    api_client,
    user,
    product,
    second_product,
):
    review1 = Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="review 1",
    )

    review2 = Review.objects.create(
        product=second_product,
        user=user,
        rating=4,
        text="review 2",
    )

    response = api_client.get(
        URL,
        {"product": product.id},
    )

    assert response.status_code == 200

    ids = [item["id"] for item in response.json()["results"]]

    assert review1.id in ids
    assert review2.id not in ids


@pytest.mark.django_db
def test_guest_cannot_create_review(
    api_client,
    product,
):
    response = api_client.post(
        URL,
        {
            "product": product.id,
            "rating": 5,
            "text": "test review",
        },
    )

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_authenticated_user_can_create_review(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL,
        {
            "product": product.id,
            "rating": 5,
            "text": "test review",
        },
    )

    assert response.status_code == 201

    review = Review.objects.get(
        product=product,
        user=user,
    )

    assert review.rating == 5
    assert review.text == "test review"


@pytest.mark.django_db
def test_user_cannot_spoof_author(
    api_client,
    user,
    another_user,
    product,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL,
        {
            "product": product.id,
            "rating": 5,
            "text": "test review",
            "user": another_user.id,
        },
    )

    assert response.status_code == 201

    review = Review.objects.get(product=product)

    assert review.user == user
    assert review.user != another_user


@pytest.mark.django_db
def test_duplicate_review_returns_400(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    first_response = api_client.post(
        URL,
        {
            "product": product.id,
            "rating": 5,
            "text": "first review",
        },
    )

    assert first_response.status_code == 201

    second_response = api_client.post(
        URL,
        {
            "product": product.id,
            "rating": 4,
            "text": "second review",
        },
    )

    assert second_response.status_code == 400
    assert "Вы уже оставляли отзыв" in str(
        second_response.json()
    )


@pytest.mark.django_db
def test_owner_can_update_review(
    api_client,
    user,
    review,
):
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        f"{URL}{review.id}/",
        {
            "rating": 4,
            "text": "updated review",
        },
    )

    assert response.status_code == 200

    review.refresh_from_db()

    assert review.rating == 4
    assert review.text == "updated review"


@pytest.mark.django_db
def test_another_user_cannot_update_review(
    api_client,
    another_user,
    review,
):
    api_client.force_authenticate(user=another_user)

    response = api_client.patch(
        f"{URL}{review.id}/",
        {
            "rating": 1,
            "text": "hacked review",
        },
    )

    assert response.status_code == 403

    review.refresh_from_db()

    assert review.rating == 5
    assert review.text == "test review"


@pytest.mark.django_db
def test_owner_can_delete_review(
    api_client,
    user,
    review,
):
    api_client.force_authenticate(user=user)

    response = api_client.delete(
        f"{URL}{review.id}/"
    )

    assert response.status_code == 204

    assert not Review.objects.filter(
        pk=review.id
    ).exists()


@pytest.mark.django_db
def test_another_user_cannot_delete_review(
    api_client,
    another_user,
    review,
):
    api_client.force_authenticate(user=another_user)

    response = api_client.delete(
        f"{URL}{review.id}/"
    )

    assert response.status_code == 403

    assert Review.objects.filter(
        pk=review.id
    ).exists()


@pytest.mark.django_db
def test_staff_can_delete_any_review(
    api_client,
    staff,
    review,
):
    api_client.force_authenticate(user=staff)

    response = api_client.delete(
        f"{URL}{review.id}/"
    )

    assert response.status_code == 204

    assert not Review.objects.filter(
        pk=review.id
    ).exists()