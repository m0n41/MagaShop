from django.urls import path
from .views_api import WishlistListCreateViews, WishlistDestroyAPIView

urlpatterns = [
    path("wishlist/", WishlistListCreateViews.as_view()),
    path("wishlist/<int:pk>/", WishlistDestroyAPIView.as_view())
]
