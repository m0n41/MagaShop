import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Category, Product


@pytest.mark.django_db
def test_catalog_html_list_still_works():
	response = APIClient().get(reverse("catalog:product_list"))

	assert response.status_code == 200
	assert response["Content-Type"].startswith("text/html")


@pytest.mark.django_db
def test_catalog_html_category_still_works():
	category = Category.objects.create(name="Смартфоны")
	Product.objects.create(
		name="Телефон",
		category=category,
		description="Описание товара",
		price=1000,
		stock=5,
		is_available=True,
		image="products/test.jpg",
	)

	response = APIClient().get(
		reverse("catalog:category_detail", kwargs={"slug": category.slug})
	)

	assert response.status_code == 200
	assert response["Content-Type"].startswith("text/html")


@pytest.mark.django_db
def test_catalog_html_product_detail_still_works():
	category = Category.objects.create(name="Смартфоны")
	product = Product.objects.create(
		name="Телефон",
		category=category,
		description="Описание товара",
		price=1000,
		stock=5,
		is_available=True,
		image="products/test.jpg",
	)

	response = APIClient().get(
		reverse("catalog:product_detail", kwargs={"slug": product.slug})
	)

	assert response.status_code == 200
	assert response["Content-Type"].startswith("text/html")
