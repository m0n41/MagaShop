from rest_framework import serializers
from orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "price", "quantity")

class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ("id", "created_at", "status", "is_paid", "total", "discount", "items")
        
    def get_total(self, obj):
        return obj.get_total_cost()