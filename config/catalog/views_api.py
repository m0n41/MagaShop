from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import (
    ProductSerializer, CategorySerializer,
    ProductDetailSerializer,
    ProductFilterSerializer
)
from .models import Product
from django.db.models import Q
from .pagination import ProductAPIListPagination
from .permission import CatalogListDetailPermission

class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductAPIListPagination
    permission_classes = [CatalogListDetailPermission]
    
    def get_queryset(self):
        queryset = Product.objects.filter(
            is_available=True,
            stock__gt=0,
            category__is_active=True
        )
        serializer = ProductFilterSerializer(
            data=self.request.query_params
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        if data.get("brand"):
            queryset = queryset.filter(
                brand=data["brand"]
            )
        
        if data.get("category"):
            queryset = queryset.filter(
                category__slug=data["category"]
            )
            
        if data.get("search"):
            queryset = queryset.filter(
                Q(name__icontains=data["search"]) |
                Q(description__icontains=data["search"])
            )
        
        if data.get("min_price") is not None:
            queryset = queryset.filter(
                price__gte=data["min_price"]
            )
            
        if data.get("max_price") is not None:
            queryset = queryset.filter(
                price__lte=data["max_price"]
            )
            
        ordering = data.get("ordering", "name")
        queryset = queryset.order_by(
            ProductFilterSerializer.ALLOWED_ORDERING[ordering],
            "id"
        )
        
        return queryset
    
class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [CatalogListDetailPermission]
    lookup_field = "slug"
    
    def get_queryset(self):
        return Product.objects.filter(is_available=True, stock__gt=0, category__is_active=True)
    
    