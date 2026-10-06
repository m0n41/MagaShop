"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "MagaShop — администрирование"
admin.site.site_title = "MagaShop admin"
admin.site.index_title = "Панель управления магазином"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('catalog/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('users/', include('users.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path("api/v1/", include("catalog.urls_api")),
    path("api/v1/", include("users.urls_api")),
    path("api/v1/", include("reviews.urls_api")),
    path("api/v1/", include("wishlist.urls_api")),
    path("api/v1/", include("cart.urls_api")),
    path("api/v1/", include("orders.urls_api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
