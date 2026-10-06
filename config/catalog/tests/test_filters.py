from decimal import Decimal

import pytest

from catalog.serializers import ProductFilterSerializer


def test_product_filter_serializer_valid_data():
	serializer = ProductFilterSerializer(data={
		"category": "smartfony",
		"brand": "Apple",
		"search": "iphone",
		"min_price": "100.00",
		"max_price": "200.00",
		"ordering": "price",
	})

	assert serializer.is_valid()
	assert serializer.validated_data["min_price"] == Decimal("100.00")
	assert serializer.validated_data["max_price"] == Decimal("200.00")


@pytest.mark.parametrize("field", ["min_price", "max_price"])
def test_product_filter_serializer_rejects_invalid_price(field):
	serializer = ProductFilterSerializer(data={field: "not-a-price"})

	assert not serializer.is_valid()
	assert field in serializer.errors


@pytest.mark.parametrize("field", ["min_price", "max_price"])
def test_product_filter_serializer_rejects_negative_price(field):
	serializer = ProductFilterSerializer(data={field: "-1.00"})

	assert not serializer.is_valid()
	assert field in serializer.errors


def test_product_filter_serializer_rejects_reversed_price_range():
	serializer = ProductFilterSerializer(data={
		"min_price": "200.00",
		"max_price": "100.00",
	})

	assert not serializer.is_valid()
	assert "non_field_errors" in serializer.errors


@pytest.mark.parametrize(
	"ordering",
	["price", "-price", "-views", "-created_at", "name"],
)
def test_product_filter_serializer_accepts_allowed_ordering(ordering):
	serializer = ProductFilterSerializer(data={"ordering": ordering})

	assert serializer.is_valid()


def test_product_filter_serializer_rejects_unknown_ordering():
	serializer = ProductFilterSerializer(data={"ordering": "price__secret"})

	assert not serializer.is_valid()
	assert "ordering" in serializer.errors


def test_product_filter_serializer_ignores_unknown_query_parameter():
	serializer = ProductFilterSerializer(data={"unexpected": "value"})

	assert serializer.is_valid()
	assert serializer.validated_data == {}
