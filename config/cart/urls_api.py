from django.urls import path
from .views_api import CartAPIView

urlpatterns = [
    path("cart/", CartAPIView.as_view())
]
