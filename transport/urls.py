from rest_framework.routers import DefaultRouter
from transport.views import OrderViewSet


router = DefaultRouter()
router.register('order', OrderViewSet, basename='order')

urlpatterns = router.urls