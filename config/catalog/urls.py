from django.urls import path, register_converter

from config.converters import UnicodeSlugConverter

from .views import (
    CategoryListView, ProductListView, 
    ProductDetailView, SearchView, 
    SimilarProductsView, ProductAddView,
)

register_converter(UnicodeSlugConverter, 'uslug')

app_name = 'catalog'

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("search/", SearchView.as_view(), name="search"),
    path("product_add/", ProductAddView.as_view(), name="product_add"),
    path("product/<uslug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/<uslug:slug>/similar/", SimilarProductsView.as_view(), name="similar_products"),
    path("<uslug:slug>/", CategoryListView.as_view(), name="category_detail"),
]
