import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


TOKEN_URL = "/api/v1/api-token-auth/"


def create_user(username="api-user", email="api-user@example.com", password="Test-pass-123"):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name="API",
        last_name="User",
    )


@pytest.mark.django_db
def test_token_endpoint_returns_token_for_existing_user():
    user = create_user()

    response = APIClient().post(TOKEN_URL, {
        "username": user.username,
        "password": "Test-pass-123",
    }, format="json")

    assert response.status_code == 200
    assert response.data["token"]


@pytest.mark.django_db
def test_token_endpoint_accepts_email_as_username():
    user = create_user()

    response = APIClient().post(TOKEN_URL, {
        "username": user.email,
        "password": "Test-pass-123",
    }, format="json")

    assert response.status_code == 200
    assert response.data["token"]


@pytest.mark.django_db
def test_token_endpoint_rejects_invalid_password():
    user = create_user()

    response = APIClient().post(TOKEN_URL, {
        "username": user.username,
        "password": "wrong-password",
    }, format="json")

    assert response.status_code == 400
    assert "token" not in response.data