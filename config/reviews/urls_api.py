from rest_framework import routers
from .views_api import ReviewViewSet

router = routers.SimpleRouter()
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = router.urls
