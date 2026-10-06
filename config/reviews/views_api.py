from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from .permission import ReviewsListPermission

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewsListPermission,)
    
    def get_queryset(self):
        queryset = Review.objects.all()
        
        product_id = self.request.query_params.get("product")
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        if self.request.user.is_staff:
            return queryset
        
        return queryset.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)