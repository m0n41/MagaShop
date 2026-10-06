import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


TOKEN_URL = "/api/v1/api-token-auth/"
CURRENT_USER_URL = "/api/v1/users/me/"


def create_user(username="api-user", email="api-user@example.com", password="Test-pass-123"):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name="API",
        last_name="User",
    )


def authenticated_client(user):
    response = APIClient().post(TOKEN_URL, {
        "username": user.username,
        "password": "Test-pass-123",
    }, format="json")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
    return client


@pytest.mark.django_db
def test_current_user_endpoint_requires_token():
    response = APIClient().get(CURRENT_USER_URL, HTTP_ACCEPT="application/json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_current_user_endpoint_returns_safe_authenticated_user_fields():
    user = create_user()

    response = authenticated_client(user).get(
        CURRENT_USER_URL,
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 200
    assert response.data == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    assert "password" not in response.data
    assert "status_user" not in response.data
    assert "photo" not in response.data


@pytest.mark.django_db
def test_current_user_endpoint_does_not_allow_user_id_override():
    current_user = create_user()
    other_user = create_user(
        username="other-user",
        email="other-user@example.com",
    )

    response = authenticated_client(current_user).get(
        f"{CURRENT_USER_URL}?user_id={other_user.id}",
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 200
    assert response.data["id"] == current_user.id
    assert response.data["email"] == current_user.email
    assert response.data["id"] != other_user.id