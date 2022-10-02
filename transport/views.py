from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from transport.models import OrderModel
from transport.serializer import OrderSerializer
from rest_framework import viewsets
    
    
class OrderViewSet(viewsets.ModelViewSet):
    """
    Vista para la creación de pedidos
    """
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.all()
    http_method_names = ['get', 'post', 'head', "delete"]
    ordering_fields = ['driver_available__driver', 'driver_available__schedule']    
    ordering = "driver_available__schedule__hour"
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_fields = {
        'driver_available__driver': ["exact"],
        "driver_available__schedule": ["hour__exact"]
    }
