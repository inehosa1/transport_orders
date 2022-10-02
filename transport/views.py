from math import dist
from datetime import datetime

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from transport.models import OrderModel
from transport.serializer import OrderSerializer, NearestDriverSerializer

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

class OrderFilter(filters.FilterSet):
    driver_available__schedule = filters.DateFromToRangeFilter(field_name='driver_available__schedule')

    class Meta:
        model = OrderModel
        fields = ['driver_available__schedule', "driver_available__driver"]

class FindNearestDriverFilter(filters.FilterSet):
    
    class Meta:
        model = OrderModel
        fields = ['driver_available__schedule', "driver_available__delivery_latitude", "driver_available__delivery_longitude"]


class OrderViewSet(viewsets.ModelViewSet):
    """
    Vista para la creación de pedidos
    """
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.select_related("driver_available").all().order_by('driver_available__schedule', 'driver_available__schedule__hour')
    http_method_names = ['get', 'post', 'head', "delete"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def search_greater_or_less_record(self, request, major_or_minor, symbol=""):
        """
        Función para buscar el primer registro hacia arriba y el primer registro hacia abajo
        """
        convert_date_schedule = datetime.strptime(request.GET.get("driver_available__schedule"), "%Y-%m-%d %H:%M")
        
        filter_data = {
            f"driver_available__schedule__{major_or_minor}": convert_date_schedule,
            f"driver_available__schedule__day": convert_date_schedule.day,
            f"driver_available__delivery_latitude__{major_or_minor}": request.GET.get("driver_available__delivery_latitude"),
            f"driver_available__delivery_longitude__{major_or_minor}": request.GET.get("driver_available__delivery_longitude")
        }
        return OrderModel.objects.filter(**filter_data).order_by(f"{symbol}driver_available__delivery_latitude", f"{symbol}driver_available__delivery_longitude").first()
  
    def calcule_dist_driver(self, request, instance):
        """
        Función para calcular la distancia entre la latitud y longitud
        """
        return dist(
            (int(request.GET.get("driver_available__delivery_latitude")), int(request.GET.get("driver_available__delivery_longitude"))),
            (instance.driver_available.delivery_latitude,instance.driver_available.delivery_longitude)
        )

    @swagger_auto_schema(operation_description="Busqueda del conductor mas cercano acorde a las cordenadas ingresadas")
    @action(detail=False, methods=['get'], filterset_class = FindNearestDriverFilter)
    def find_nearest_driver(self, request):
        """
        Busqueda del conductor mas cercano acorde a las cordenadas ingresadas en una fecha y hora
        """        
        serializer_neares_driver = NearestDriverSerializer(data=request.GET)
        
        if not serializer_neares_driver.is_valid():
            return Response(serializer_neares_driver.errors, status=status.HTTP_400_BAD_REQUEST)

        # Se obtiene el primer registro mayor que la latitud y longitud ingresada
        instance_greater_closest_drivers = self.search_greater_or_less_record(request, "gte")
        
        # Se obtiene el segundo registro mayor que la latitud y longitud ingresada
        instance_less_closest_drivers = self.search_greater_or_less_record(request, "lte", "-")
        
        greater_closest_drivers = None
        
        if instance_greater_closest_drivers:
            # Se comparan la cordenadas ingresadas del mayor registro para obtener la distancia
            greater_closest_drivers = self.calcule_dist_driver(request, instance_greater_closest_drivers)

        less_closest_drivers = None
        
        if instance_less_closest_drivers:
            # Se comparan la cordenadas ingresadas del menor registro para obtener la distancia
            less_closest_drivers= self.calcule_dist_driver(request, instance_less_closest_drivers)

        # Se validan las instancias ya que cuando la coincidencia es 0.0 no lo reconoce
        if isinstance(greater_closest_drivers, float) and isinstance(less_closest_drivers, float):
            # El registro que sus coordenadas esten mas cerca es el que se retorna al usuario
            if greater_closest_drivers < less_closest_drivers:            
                serializer = self.get_serializer(instance_greater_closest_drivers)
            else:
                serializer = self.get_serializer(instance_less_closest_drivers)
        elif isinstance(greater_closest_drivers, float):
            serializer = self.get_serializer(instance_greater_closest_drivers)
        elif isinstance(less_closest_drivers, float):
            serializer = self.get_serializer(instance_less_closest_drivers)
        else:
            return Response({"message": "No se encuentran conductores disponibles en la fecha ingresada"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.data)