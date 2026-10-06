from django.urls import path, register_converter

from config.converters import UnicodeSlugConverter

from .views_api import ProductListAPIView, ProductDetailAPIView

register_converter(UnicodeSlugConverter, "api_uslug")

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name='product-list'),
    path("products/<api_uslug:slug>/", ProductDetailAPIView.as_view(), name='product-detail')
]
