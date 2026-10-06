from .models import Wishlist
from .serializer import WishlistSerializer
from .permission import WishlistPermission
from rest_framework.generics import ListCreateAPIView, DestroyAPIView

class WishlistListCreateViews(ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = (WishlistPermission, )
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WishlistDestroyAPIView(DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = (WishlistPermission, )
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)