from rest_framework import serializers
from .models import Wishlist

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["product"]
        
    def validate(self, attrs):
        request = self.context.get("request")
        
        if request and request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(
                product=attrs["product"],
                user=request.user,
            )

            if self.instance:
                wishlist = wishlist.exclude(pk=self.instance.pk)
                
            if wishlist.exists():
                raise serializers.ValidationError(
                    "Вы уже добавили в избранное."
                )
        
        return attrs 