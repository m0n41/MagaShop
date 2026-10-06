from django.urls import path
from .views import WishlistView, wishlist_toggle

app_name = 'wishlist'

urlpatterns = [
    path("", WishlistView.as_view(), name="list"),
    path("toggle/<int:product_id>/", wishlist_toggle, name="toggle"),
]
