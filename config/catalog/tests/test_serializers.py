from django.test import TestCase
from catalog.models import Category, Product, ProductImage
from catalog.serializers import ProductDetailSerializer, ProductSerializer
import pytest

# Test Product Serializer

@pytest.mark.django_db
def test_product_serializer():
    category = Category.objects.create(name="Машина")
    product = Product.objects.create(
        name="Колесо",
        category=category,
        description="Описание",
        price=1000,
        stock=5,
        is_available=True,
        image="products/test.jpg",
    )
    serializer = ProductSerializer(product)
    data = serializer.data
    
    assert data["category"]["id"] == category.id
    assert data["category"]["name"] == category.name
    assert data["category"]["slug"] == category.slug

@pytest.mark.django_db
def test_product_tags():
    category = Category.objects.create(name="Машина")
    product = Product.objects.create(
        name="Колесо",
        category=category,
        description="Описание",
        price=1000,
        stock=5,
        is_available=True,
        image="products/test.jpg",
    )
    product.tags.add("лето", "новинка", "скидка")
    serializer = ProductSerializer(product)
    data = serializer.data
    
    assert data["tags"] == ["лето", "новинка", "скидка"]
    
@pytest.mark.django_db
def test_product_stock():
    category = Category.objects.create(name="Машина")
    product_one = Product.objects.create(
        name="Колесо",
        category=category,
        description="Описание",
        price=1000,
        stock=5,
        is_available=True,
        image="products/test.jpg",
    )
    product_two = Product.objects.create(
        name="Руль",
        category=category,
        description="Описание",
        price=1000,
        stock=0,
        is_available=True,
        image="products/test.jpg",
    )
    serializer_one = ProductSerializer(product_one)
    serializer_two = ProductSerializer(product_two)
    data_one = serializer_one.data
    data_two = serializer_two.data
    
    assert data_one["in_stock"] == True
    assert data_two["in_stock"] == False

@pytest.mark.django_db
def test_product_detail_serializer_images():
    category = Category.objects.create(name="Машина")
    product = Product.objects.create(
        name="Колесо",
        category=category,
        description="Описание",
        price=1000,
        stock=5,
        is_available=True,
        image="products/test.jpg",
    )
    ProductImage.objects.create(
        product=product,
        image="products/test-main.jpg",
        alt_text="Главное изображение",
        is_main=True,
    )
    ProductImage.objects.create(
        product=product,
        image="products/test-side.jpg",
        alt_text="Вид сбоку",
        is_main=False,
    )

    data = ProductDetailSerializer(product).data

    assert len(data["images"]) == 2
    assert data["images"][0]["image"].endswith("products/test-main.jpg")
    assert data["images"][0]["alt_text"] == "Главное изображение"
    assert data["images"][0]["is_main"] is True
    assert data["images"][1]["alt_text"] == "Вид сбоку"
    assert data["images"][1]["is_main"] is False

@pytest.mark.django_db
def test_product_detail_serializer_without_extra_images():
    category = Category.objects.create(name="Машина")
    product = Product.objects.create(
        name="Колесо",
        category=category,
        description="Описание",
        price=1000,
        stock=5,
        is_available=True,
        image="products/test.jpg",
    )

    data = ProductDetailSerializer(product).data

    assert data["images"] == []