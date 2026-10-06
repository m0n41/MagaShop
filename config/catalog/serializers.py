from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")
        
class ProductSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ("id", "name", "slug", "category", "brand", "description", "price", "in_stock", "old_price", "is_available", "image", "tags")
    
    def get_tags(self, obj):
        return list(obj.tags.values_list("name", flat=True))
    
    def get_in_stock(self, obj):
        return True if obj.stock > 0 else False

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("image", "alt_text", "is_main")

class ProductDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ("id", "name", "slug", "category", "brand", "description", "price", "in_stock", "old_price", "is_available", "image", "tags", "images")
        
    def get_tags(self, obj):
        return list(obj.tags.values_list("name", flat=True))
    
    def get_in_stock(self, obj):
        return True if obj.stock > 0 else False

class ProductFilterSerializer(serializers.Serializer):
    
    ALLOWED_ORDERING = {
        "price": "price",
        "-price": "-price",
        "-views": "-views",
        "-created_at": "-created_at",
        "name": "name",
    }
    
    category = serializers.CharField(required=False)
    brand = serializers.CharField(required=False)
    search = serializers.CharField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    ordering = serializers.CharField(required=False)
    
    def validate_category(self, value):
        if not value:
            raise serializers.ValidationError("Категория не указана")
        return value
    
    def validate_brand(self, value):
        if not value:
            raise serializers.ValidationError("Бренд не указан")
        return value
    
    def validate_search(self, value):
        if not value:
            raise serializers.ValidationError("Поиск не указан")
        return value
    
    def validate_min_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Минимальная цена не указана")
        return value
    
    def validate_max_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Максимальная цена не указана")
        return value
    
    def validate_ordering(self, value):
        if value not in self.ALLOWED_ORDERING:
            raise serializers.ValidationError(
                f"Допустимые значения: {', '.join(self.ALLOWED_ORDERING)}"
            )
        return value
        
    def validate(self, data):
        min_price = data.get("min_price")
        max_price = data.get("max_price")
        
        if (min_price is not None and max_price is not None
            and min_price > max_price
        ):
            raise serializers.ValidationError(
                "Минимальная цена не может превышать максимальную"
            )

        return data