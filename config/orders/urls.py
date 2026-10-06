from django.urls import path
from .views import OrderCreateView, OrderBuyView, OrderDetailView, OrderListView

app_name = 'orders'

urlpatterns = [
    path('order_list/', OrderListView.as_view(), name='list'),
    path('order_list/<int:pk>/', OrderDetailView.as_view(), name='detail'),
    path('order_create/', OrderCreateView.as_view(), name='create'),
    path('order_buy/', OrderBuyView.as_view(), name='buy'),
]
