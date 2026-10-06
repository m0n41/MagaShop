from .views import cart_add, cart_remove, cart_clear, cart_detail, buy_now, apply_coupon, remove_coupon
from django.urls import path

app_name = 'cart'

urlpatterns = [
    path("add/<int:product_id>/", cart_add, name='add'),
    path("remove/<int:product_id>/", cart_remove, name='remove'),
    path("clear/", cart_clear, name='clear'),
    path("detail/", cart_detail, name='detail'),
    path("buy-now/<int:product_id>/", buy_now, name='buy_now'),
    path("apply-coupon/", apply_coupon, name="apply_coupon"),
    path("remove-coupon/", remove_coupon, name="remove_coupon"),
]
