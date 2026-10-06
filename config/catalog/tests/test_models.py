from django.test import TestCase
from catalog.models import Category, Product, ProductImage
import pytest

# Test Category Models

@pytest.mark.django_db
def test_category_creation():
    category = Category.objects.create(name="test")
    
    assert category.slug == "test"
    
@pytest.mark.django_db
def test_category_str():
    category = Category.objects.create(name="Электроника")
    
    assert str(category) == "Электроника"
    
# Test Product Models

@pytest.mark.django_db
def test_product_creation():
    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(
        name="Телефон",
        category=category,
        description="Описание",
        price=1000,
        image="products/test.jpg",
    )
    
    assert product.slug == "телефон"
    
@pytest.mark.django_db
def test_discount_percent():
    category = Category.objects.create(name="Детское")
    product = Product.objects.create(
        name="Игрушка",
        category=category,
        description="Описание",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )
    
    assert product.discount_percent == 20

@pytest.mark.django_db
def test_discount_percent_revers_one():
    category = Category.objects.create(name="Детское")
    product = Product.objects.create(
        name="Игрушка",
        category=category,
        description="Описание",
        price=0,
        image="products/test.jpg",
    )
    
    assert product.discount_percent == 0
    
@pytest.mark.django_db
def test_discount_percent_revers_two():
    category = Category.objects.create(name="Детское")
    product = Product.objects.create(
        name="Игрушка",
        category=category,
        description="Описание",
        price=1000,
        old_price=800,
        image="products/test.jpg",
    )
    
    assert product.discount_percent == 0
    
@pytest.mark.django_db
def test_product_available():
    category = Category.objects.create(name="машина")
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
        name="Шина",
        category=category,
        description="Описание",
        price=1000,
        stock=0,
        is_available=True,
        image="products/test.jpg",
    )
    product_three = Product.objects.create(
        name="Воздух",
        category=category,
        description="Описание",
        price=1000,
        stock=5,
        is_available=False,
        image="products/test.jpg",
    )
    
    available_products = Product.available.all()
    
    assert product_one in available_products
    assert product_two not in available_products
    assert product_three not in available_products

@pytest.mark.django_db
def test_product_image():
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
    product_image = ProductImage.objects.create(
        product=product,
        image="products/test.jpg",
        is_main=False,
        alt_text="Красное колесо",
    )
    product_image_two = ProductImage.objects.create(
        product=product,
        image="products/test.jpg",
        is_main=False,
    )
    
    assert str(product_image) == "Красное колесо"
    assert str(product_image_two) == product_image_two.product.name + " " + "image"