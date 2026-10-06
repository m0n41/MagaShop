from rest_framework.views import APIView
from rest_framework.response import Response
from catalog.models import Product
from .cart import Cart
from .serializer import CartItemSerializer

class CartAPIView(APIView):
    def get(self, request):
        cart = Cart(request)
        cart_list = []
        total_price = 0
        
        for item in cart:
            cart_list.append(
                {
                    "id": item["product"].id,
                    "name": item["product"].name,
                    "price": item["product"].price,
                    "quantity": item["quantity"],
                    "total": item["product"].price * item["quantity"],
                }
            )
            
            total_price += item["product"].price * item["quantity"]
            
        return Response({
                "cart": CartItemSerializer(cart_list, many=True).data,
                "total_price": total_price,
            })
        
    def post(self, request):
        if "product_id" not in request.data:
            return Response({"message": "Не введен параметр!"}, status=400)
        
        try:
            quantity = int(request.data.get("quantity"))
        except (TypeError, ValueError):
            return Response({"message": "Количество должно быть целым числом!"},status=400)

        if quantity <= 0:
            return Response({"message": "Некорректное количество!"},status=400)
        
        try:
            product = Product.objects.get(id=request.data.get("product_id"))
        except Product.DoesNotExist:
            return Response({"message": "Такого продукта нет!"}, status=404)
        cart = Cart(request)
        cart.add(product=product, quantity=quantity)
        return Response({"message": "Продукт добавлен в корзину"})
    
    def patch(self, request):
        if "product_id" not in request.data:
            return Response({"message": "Не введен параметр!"}, status=400)
        
        try:
            quantity = int(request.data.get("quantity"))
        except (TypeError, ValueError):
            return Response({"message": "Количество должно быть целым числом!"},status=400)

        if quantity <= 0:
            return Response({"message": "Некорректное количество!"},status=400)
        
        try:
            product = Product.objects.get(id=request.data.get("product_id"))
        except Product.DoesNotExist:
            return Response({"message": "Такого продукта нет!"}, status=404)
        
        cart = Cart(request)
        
        if str(product.id) not in cart.cart:
            return Response({"message": "Товар отсутствует в корзине!"},status=404)
        
        cart.add(product=product, quantity=quantity, update_quantity=True)
        return Response({"message": "Количество продукта изменено"})
    
    def delete(self, request):
        if "product_id" not in request.data:
            return Response({"message": "Не введен параметр!"}, status=400)
                
        try:
            product = Product.objects.get(id=request.data.get("product_id"))
        except Product.DoesNotExist:
            return Response({"message": "Такого продукта нет!"}, status=404)
        
        cart = Cart(request)
        if str(product.id) not in cart.cart:
            return Response({"message": "Товар отсутствует в корзине!"},status=404)
        
        cart.remove(product)
        return Response({"message": "Товар удален из корзины"})