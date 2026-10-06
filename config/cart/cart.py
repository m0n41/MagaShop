from catalog.models import Product
from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart
    
    def save(self):
        self.session.modified = True
    
    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if update_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()
        
    def remove(self, product, quantity=None):
        product_id = str(product.id)
        if product_id not in self.cart:
            return
        if quantity is None or quantity >= self.cart[product_id]["quantity"]:
            del self.cart[product_id]
        else:
            self.cart[product_id]["quantity"] -= quantity
        self.save()
            
    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        products_map = {str(p.id): p for p in products}
        
        for product_id, data in self.cart.items():
            price = Decimal(data["price"])
            quantity = data["quantity"]
            yield {
                "product": products_map[product_id],
                "price": price,
                "quantity": quantity,
                "total_price": price * quantity,
            }
    
    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())
    
    @property
    def get_total_price(self):
        subtotal = sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())
        coupon_id = self.session.get("coupon_id")
        if coupon_id:
            from coupon.models import Coupon
            try:
                coupon = Coupon.objects.get(pk=coupon_id)
                if coupon.is_valid():
                    if coupon.min_order_amount is None or subtotal >= coupon.min_order_amount:
                        discount_amount = subtotal * (Decimal(coupon.discount) / Decimal(100))
                        return subtotal - discount_amount
            except Coupon.DoesNotExist:
                pass
        return subtotal

    def clear(self):
        del self.session["cart"]
        self.save()
        