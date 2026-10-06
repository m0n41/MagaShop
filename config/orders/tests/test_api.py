from decimal import Decimal
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from catalog.models import Category, Product
from coupon.models import Coupon
from orders.models import Order, OrderItem
from users.models import User
from django.core import mail


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="user",
        email="user@test.com",
        password="password123",
    )


@pytest.fixture
def second_user(db):
    return User.objects.create_user(
        username="second_user",
        email="second@test.com",
        password="password123",
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff",
        email="staff@test.com",
        password="password123",
        is_staff=True,
    )


@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def second_client(second_user):
    client = APIClient()
    client.force_authenticate(user=second_user)
    return client


@pytest.fixture
def staff_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Test category",
        slug="test-category",
    )


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Test product",
        slug="test-product",
        category=category,
        description="Test description",
        price=Decimal("2000.00"),
        stock=10,
        is_available=True,
        image="products/test.jpg",
    )


@pytest.fixture
def order_data():
    return {
        "first_name": "Бадрудин",
        "last_name": "Магомедов",
        "email": "user@example.com",
        "phone": "+79999999999",
        "address": "Test address",
        "city": "Ростов-на-Дону",
    }


@pytest.fixture
def set_cart(client, product):
    session = client.session

    session["cart"] = {
        str(product.id): {
            "quantity": 1,
            "price": str(product.price),
        }
    }

    session.save()


@pytest.fixture
def coupon(db):
    now = timezone.now()

    return Coupon.objects.create(
        code="SALE10",
        discount=10,
        valid_from=now - timezone.timedelta(days=1),
        valid_to=now + timezone.timedelta(days=1),
        is_active=True,
    )


@pytest.fixture
def order(db, user, product):
    order = Order.objects.create(
        user=user,
        first_name="Бадрудин",
        last_name="Магомедов",
        email="user@example.com",
        phone="+79999999999",
        address="Test address",
        city="Ростов-на-Дону",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        price=product.price,
        quantity=1,
    )

    return order


@pytest.fixture
def second_order(db, second_user, product):
    order = Order.objects.create(
        user=second_user,
        first_name="Second",
        last_name="User",
        email="second@example.com",
        phone="+79999999998",
        address="Second address",
        city="Москва",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        price=product.price,
        quantity=1,
    )

    return order


@pytest.mark.django_db
class TestOrderAPIView:

    def test_create_order(
        self,
        user,
        client,
        product,
        order_data,
        set_cart,
    ):
        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 200
        assert Order.objects.count() == 1

        order = Order.objects.first()

        assert order.user == user
        assert order.is_paid is False
        assert order.status == "new"

        item = order.items.first()

        assert item.product == product
        assert item.quantity == 1
        assert item.price == product.price

    def test_empty_cart(
        self,
        client,
        order_data,
    ):
        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 400
        assert response.data["message"] == "Корзина пуста!"

    def test_insufficient_stock(
        self,
        client,
        product,
        order_data,
        set_cart,
    ):
        product.stock = 0
        product.save(update_fields=["stock"])

        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 400
        assert response.data["message"] == (
            "Недостаточно товара в наличии!"
        )

    def test_current_price_is_used_at_checkout(
        self,
        client,
        product,
        order_data,
        set_cart,
    ):
        product.price = Decimal("2500.00")
        product.save(update_fields=["price"])

        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 200

        order_item = OrderItem.objects.first()

        assert order_item.price == Decimal("2500.00")

    def test_coupon_discount(
        self,
        client,
        product,
        order_data,
        set_cart,
        coupon,
    ):
        session = client.session
        session["coupon_id"] = coupon.id
        session.save()

        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 200

        order = Order.objects.first()

        assert order.discount == Decimal("200.00")

    def test_cart_and_coupon_are_cleared(
        self,
        client,
        product,
        order_data,
        set_cart,
        coupon,
    ):
        session = client.session
        session["coupon_id"] = coupon.id
        session.save()

        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 200

        session = client.session

        assert "cart" not in session
        assert "coupon_id" not in session

    def test_invalid_quantity(
        self,
        client,
        product,
        order_data,
    ):
        session = client.session

        session["cart"] = {
            str(product.id): {
                "quantity": 0,
                "price": str(product.price),
            }
        }

        session.save()

        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 400
        assert response.data["message"] == (
            "Количество продукта должно быть больше 0!"
        )

    def test_invalid_coupon(
        self,
        client,
        product,
        order_data,
        set_cart,
    ):
        session = client.session
        session["coupon_id"] = 999999
        session.save()

        response = client.post(
            "/api/v1/orders/",
            order_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.data["message"] == "Купон не найден!"

    def test_get_orders_requires_authentication(self):
        client = APIClient()

        response = client.get("/api/v1/orders/")

        assert response.status_code == 401

    def test_get_orders_returns_only_current_user_orders(
        self,
        client,
        order,
        second_order,
    ):
        response = client.get("/api/v1/orders/")

        assert response.status_code == 200

        orders = response.data["orders"]

        assert len(orders) == 1
        assert orders[0]["id"] == order.id

    def test_get_order_detail(
        self,
        client,
        order,
        product,
    ):
        response = client.get(
            f"/api/v1/orders/{order.id}/"
        )

        assert response.status_code == 200

        data = response.data["order"]

        assert data["id"] == order.id
        assert data["status"] == order.status
        assert data["is_paid"] is False
        assert data["discount"] == "0.00"
        assert data["total"] == Decimal("2000.00")

        assert len(data["items"]) == 1
        assert data["items"][0]["product"] == product.id
        assert data["items"][0]["price"] == "2000.00"
        assert data["items"][0]["quantity"] == 1

    def test_get_foreign_order_forbidden(
        self,
        client,
        second_order,
    ):
        response = client.get(
            f"/api/v1/orders/{second_order.id}/"
        )

        assert response.status_code == 403
    
    def test_order_sends_email(
        self,
        client,
        order_data,
        set_cart,
        django_capture_on_commit_callbacks,
    ):
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                "/api/v1/orders/",
                order_data,
                format="json",
            )

        assert response.status_code == 200
        assert len(mail.outbox) == 1

        email = mail.outbox[0]

        assert email.subject == "Заказ успешно создан"
        assert email.to == [order_data["email"]]
        assert "успешно создан" in email.body
        
    def test_order_error_does_not_send_email(
        self,
        client,
        product,
        order_data,
        set_cart,
        django_capture_on_commit_callbacks,
    ):
        product.stock = 0
        product.save(update_fields=["stock"])

        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                "/api/v1/orders/",
                order_data,
                format="json",
            )

        assert response.status_code == 400
        assert len(mail.outbox) == 0