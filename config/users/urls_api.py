from django.urls import path, include
from .views_api import UserListAPIView
from rest_framework.authtoken import views

urlpatterns = [
    path("api-token-auth/", views.obtain_auth_token),
    path("users/me/", UserListAPIView.as_view()),
]