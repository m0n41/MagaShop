from django.urls import path
from .views_api import OrderAPIView, OrderDetailAPIView

urlpatterns = [
    path("orders/", OrderAPIView.as_view()),
    path("orders/<int:pk>/", OrderDetailAPIView.as_view())
]
