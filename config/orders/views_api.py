from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from cart.cart import Cart
from django.db import transaction
from catalog.models import Product
from coupon.models import Coupon
from orders.models import Order, OrderItem
from .serializer import OrderSerializer
from .permission import OrderDetailPermission
from django.core.mail import send_mail

class OrderAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "Пользователь не авторизован!"}, status=401)
        
        orders = Order.objects.filter(user=request.user)
        return Response({"orders": OrderSerializer(orders, many=True).data})
        
            
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "Пользователь не авторизован!"}, status=401)
        
        cart = Cart(request)
        if not cart.cart:
            return Response({"message": "Корзина пуста!"}, status=400)
        
        required_fields = ["first_name", "last_name", "email", "phone", "address", "city"]

        for field in required_fields:
            if field not in request.data:
                return Response({"message": f"Не введен параметр: {field}"}, status=400)
            
        with transaction.atomic():
            subtotal = Decimal("0")
            products = []
            for item in cart:
                try:
                    product = Product.objects.select_for_update().get(pk=item["product"].pk)
                except Product.DoesNotExist:
                    return Response({"message": "Такого продукта нет!"}, status=404)
                quantity = item["quantity"]
                
                if quantity <= 0:
                    return Response({"message": "Количество продукта должно быть больше 0!"}, status=400)
                
                if product.stock < quantity:
                    return Response({"message": "Недостаточно товара в наличии!"}, status=400)
                
                products.append((product, quantity))
                subtotal += product.price * quantity
                
        
            discount = Decimal("0")
            coupon_id = request.session.get("coupon_id")
            
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(pk=coupon_id)
                except Coupon.DoesNotExist:
                    return Response({"message": "Купон не найден!"}, status=404)
                
                if not coupon.is_valid():
                    return Response({"message": "Купон недействителен или истёк!"}, status=400)
                
                if coupon.min_order_amount is not None and subtotal < coupon.min_order_amount:
                    return Response({"message": f"Минимальная сумма заказа для купона: {coupon.min_order_amount}"}, status=400)
                
                discount = subtotal * Decimal(coupon.discount) / Decimal("100")
        
            order = Order.objects.create(
                user=request.user,
                first_name=request.data["first_name"],
                last_name=request.data["last_name"],
                email=request.data["email"],
                phone=request.data["phone"],
                address=request.data["address"],
                city=request.data["city"],
                discount=discount,
            )
            
            for product, quantity in products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity,
                )
                
                product.stock -= quantity
                product.save(update_fields=["stock"])
        
        transaction.on_commit(
            lambda: send_mail(
                subject="Заказ успешно создан",
                message=f"Ваш заказ №{order.id} успешно создан.",
                from_email=None,
                recipient_list=[order.email],
            )
        )
        
        cart.clear()
        request.session.pop("coupon_id", None)
        return Response({"message": "Заказ успешно создан!", "order_id": order.id,})
    
class OrderDetailAPIView(APIView):
    permission_classes = (OrderDetailPermission, )
    
    def get(self, request, pk):
        
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"message": "Заказ не найден!"}, status=404)
        
        self.check_object_permissions(request, order)
        return Response({"order": OrderSerializer(order).data})