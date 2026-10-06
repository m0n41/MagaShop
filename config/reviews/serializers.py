from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "product", "rating", "text"]
        
    def validate_rating(self, value):
        if value in [1, 2, 3, 4, 5]:
            return value
        raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
    
    def validate(self, attrs):
        request = self.context.get("request")

        if request and request.user.is_authenticated and self.instance is None:
            reviews = Review.objects.filter(
                product=attrs["product"],
                user=request.user,
            )

            if reviews.exists():
                raise serializers.ValidationError(
                    "Вы уже оставляли отзыв на этот товар."
                )

        return attrs