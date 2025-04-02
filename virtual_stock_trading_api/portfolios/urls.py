from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PortfolioViewSet, PositionViewSet

router = DefaultRouter()
router.register(r'', PortfolioViewSet, basename='portfolio')
router.register(r'positions', PositionViewSet, basename='position')

urlpatterns = router.urls