import pytest
from reviews.models import Review
from catalog.models import Product, Category
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

@pytest.mark.django_db
def test_models_create_review():
    user = User.objects.create(
        username="testuser",
        email="testuser@mail.ru",
        is_staff=False,
        is_active=True,
    )
    category = Category.objects.create(name="testcategory")
    product = Product.objects.create(
        name="testproduct",
        category=category,
        description="testproductdescription",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )
    review = Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="testreviewtext"
    )
    
    assert isinstance(review, Review)
    assert review.product == product
    assert review.user == user
    assert review.rating == 5
    assert review.text == "testreviewtext"
    assert review.is_active == True
    
@pytest.mark.django_db
def test_models_unique():
    user = User.objects.create(
        username="testuser",
        email="testuser@mail.ru",
        is_staff=False,
        is_active=True,
    )
    category = Category.objects.create(name="testcategory")
    product = Product.objects.create(
        name="testproduct",
        category=category,
        description="testproductdescription",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )
    review = Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="testreviewtext"
    )
    
    with pytest.raises(IntegrityError):
        review1 = Review.objects.create(
            product=product,
            user=user,
            rating=5,
            text="testreviewtext"
        )
        
@pytest.mark.django_db
def test_models_different_goods():
    user = User.objects.create(
        username="testuser",
        email="testuser@mail.ru",
        is_staff=False,
        is_active=True,
    )
    category = Category.objects.create(name="testcategory")
    product = Product.objects.create(
        name="testproduct",
        category=category,
        description="testproductdescription",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )
    category1 = Category.objects.create(name="testcategory1")
    product1 = Product.objects.create(
        name="testproduct1",
        category=category1,
        description="testproductdescription1",
        price=800,
        old_price=1000,
        image="products/test.jpg",
    )
    review = Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text="testreviewtext"
    )
    review1 = Review.objects.create(
        product=product1,
        user=user,
        rating=5,
        text="testreviewtext"
    )
    
    assert review.user == user
    assert review1.user == user

    assert review.product == product
    assert review1.product == product1