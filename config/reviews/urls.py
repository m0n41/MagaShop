from django.urls import path, register_converter

from config.converters import UnicodeSlugConverter

from .views import ReviewCreteUser

register_converter(UnicodeSlugConverter, 'uslug')

app_name = 'reviews'

urlpatterns = [
    path("product/<uslug:slug>/review/", ReviewCreteUser.as_view(), name="create"),
]
