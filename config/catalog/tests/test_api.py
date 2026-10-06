from datetime import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product, ProductImage


def create_category(name="Электроника", is_active=True):
    return Category.objects.create(name=name, is_active=is_active)


def create_product(category, name, price=1000, brand="Test", **kwargs):
    return Product.objects.create(
        name=name,
        category=category,
        brand=brand,
        description=kwargs.pop("description", "Описание товара"),
        price=price,
        stock=kwargs.pop("stock", 5),
        is_available=kwargs.pop("is_available", True),
        views=kwargs.pop("views", 0),
        image="products/test.jpg",
        **kwargs,
    )


@pytest.mark.django_db
def test_product_list_anonymous():
    category = create_category()
    product = create_product(category, "Телефон")
    product.tags.add("новинка", "популярное")

    response = APIClient().get(reverse("product-list"), HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    result = response.data["results"][0]
    assert result["id"] == product.id
    assert result["category"] == {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
    }
    assert result["tags"] == ["новинка", "популярное"]
    assert result["in_stock"] is True
    assert "stock" not in result
    assert result["image"].endswith("products/test.jpg")


@pytest.mark.django_db
def test_product_list_only_returns_visible_products():
    active_category = create_category()
    inactive_category = create_category("Архив", is_active=False)
    visible_product = create_product(active_category, "Доступный")
    create_product(active_category, "Нет остатка", stock=0)
    create_product(active_category, "Скрытый товар", is_available=False)
    create_product(inactive_category, "Неактивная категория")

    response = APIClient().get(reverse("product-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [visible_product.id]


@pytest.mark.django_db
def test_product_list_combines_filters():
    category = create_category("Смартфоны")
    matching_product = create_product(
        category,
        "iPhone 15 Pro",
        price=Decimal("90000.00"),
        brand="Apple",
        description="Профессиональный смартфон",
    )
    create_product(category, "iPhone SE", price=Decimal("40000.00"), brand="Apple")
    create_product(category, "Galaxy Pro", price=Decimal("90000.00"), brand="Samsung")

    response = APIClient().get(reverse("product-list"), {
        "category": category.slug,
        "brand": "Apple",
        "search": "профессиональный",
        "min_price": "80000",
        "max_price": "100000",
    })

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == matching_product.id


@pytest.mark.django_db
def test_product_list_unknown_category_returns_empty_results():
    create_product(create_category(), "Телефон")

    response = APIClient().get(reverse("product-list"), {"category": "missing-category"})

    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.parametrize(
    "query_params",
    [
        {"min_price": "not-a-price"},
        {"min_price": "-1"},
        {"max_price": "-1"},
        {"min_price": "100", "max_price": "50"},
        {"ordering": "price__secret"},
    ],
)
@pytest.mark.django_db
def test_product_list_invalid_query_returns_400(query_params):
    response = APIClient().get(reverse("product-list"), query_params)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("ordering", "expected_names"),
    [
        ("price", ["Zebra", "Middle", "Alpha"]),
        ("-price", ["Alpha", "Middle", "Zebra"]),
        ("-views", ["Alpha", "Middle", "Zebra"]),
        ("-created_at", ["Alpha", "Middle", "Zebra"]),
        ("name", ["Alpha", "Middle", "Zebra"]),
    ],
)
@pytest.mark.django_db
def test_product_list_ordering(ordering, expected_names):
    category = create_category()
    zebra = create_product(category, "Zebra", price=10, views=1)
    middle = create_product(category, "Middle", price=20, views=2)
    alpha = create_product(category, "Alpha", price=30, views=3)
    created_dates = {
        zebra.id: datetime(2024, 1, 1, tzinfo=timezone.get_current_timezone()),
        middle.id: datetime(2024, 1, 2, tzinfo=timezone.get_current_timezone()),
        alpha.id: datetime(2024, 1, 3, tzinfo=timezone.get_current_timezone()),
    }
    for product_id, created_at in created_dates.items():
        Product.objects.filter(pk=product_id).update(created_at=created_at)

    response = APIClient().get(reverse("product-list"), {"ordering": ordering})

    assert response.status_code == 200
    assert [item["name"] for item in response.data["results"]] == expected_names


@pytest.mark.django_db
def test_product_list_ordering_uses_id_as_tiebreaker():
    category = create_category()
    first_product = create_product(category, "First", price=100)
    second_product = create_product(category, "Second", price=100)

    response = APIClient().get(reverse("product-list"), {"ordering": "price"})

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [
        first_product.id,
        second_product.id,
    ]


@pytest.mark.django_db
def test_product_list_pagination_limit_offset_and_max_limit():
    category = create_category()
    products = [
        create_product(category, f"Товар {number:02}", price=number)
        for number in range(12)
    ]

    default_response = APIClient().get(reverse("product-list"))
    limited_response = APIClient().get(reverse("product-list"), {
        "limit": 1,
        "offset": 1,
    })
    max_limit_response = APIClient().get(reverse("product-list"), {
        "limit": 100,
        "offset": 0,
    })

    assert default_response.status_code == 200
    assert default_response.data["count"] == 12
    assert len(default_response.data["results"]) == 3
    assert default_response.data["next"] is not None
    assert default_response.data["previous"] is None
    assert limited_response.status_code == 200
    assert limited_response.data["results"][0]["id"] == products[1].id
    assert len(max_limit_response.data["results"]) == 10


@pytest.mark.django_db
def test_product_detail_anonymous_returns_images():
    category = create_category()
    product = create_product(category, "Телефон")
    product_image = ProductImage.objects.create(
        product=product,
        image="products/phone-side.jpg",
        alt_text="Вид сбоку",
        is_main=False,
    )

    response = APIClient().get(
        reverse("product-detail", kwargs={"slug": product.slug}),
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 200
    assert response.data["id"] == product.id
    assert response.data["slug"] == product.slug
    assert len(response.data["images"]) == 1
    assert response.data["images"][0]["image"].endswith("products/phone-side.jpg")
    assert response.data["images"][0]["alt_text"] == product_image.alt_text
    assert response.data["images"][0]["is_main"] is False


@pytest.mark.django_db
def test_product_detail_unknown_slug_returns_404():
    response = APIClient().get(
        reverse("product-detail", kwargs={"slug": "missing-product"}),
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_product_detail_hidden_product_returns_404():
    category = create_category()
    unavailable_product = create_product(
        category,
        "Недоступный товар",
        is_available=False,
    )

    response = APIClient().get(
        reverse("product-detail", kwargs={"slug": unavailable_product.slug})
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_product_detail_does_not_increment_views():
    category = create_category()
    product = create_product(category, "Телефон", views=7)

    response = APIClient().get(
        reverse("product-detail", kwargs={"slug": product.slug}),
        HTTP_ACCEPT="application/json",
    )
    product.refresh_from_db()

    assert response.status_code == 200
    assert product.views == 7