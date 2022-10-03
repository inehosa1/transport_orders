import requests
from math import dist
from django.db.models import Q
from rest_framework import serializers
from transport.models import DriverAvailableModel, OrderModel
from django.utils import timezone

class DriverAvailableSerializer(serializers.ModelSerializer):
    """
    Serializador para la asignación de pedidos a los conductores
    """
    schedule = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    def validate_schedule(self, schedule):
        """
        Validaciónes adicionales para la fecha
        """
        schedule_errors = []
        
        if schedule.minute != 0:
            schedule_errors.append("La fecha de entrega debe ser en horas exactas")
                    
        if timezone.now() >= schedule:
            schedule_errors.append("La fecha debe ser mayor o igual a la actual para asignar un pedido")
    
        if schedule_errors:
            raise serializers.ValidationError(", ".join(schedule_errors))
        return schedule

    class Meta:
        model = DriverAvailableModel
        fields = ["schedule", "delivery_latitude", "delivery_longitude", "driver"]
        read_only_fields = ('driver',)
        

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializador para la creación de pedidos
    """
    driver_available = DriverAvailableSerializer()
    
    def get_list_drivers(self):
        """
        Se obtiene la carga inicial de conductores de la api externa
        """
        try:
            response = requests.get(
                'https://gist.githubusercontent.com/jeithc/96681e4ac7e2b99cfe9a08ebc093787c/raw/632ca4fc3ffe77b558f467beee66f10470649bb4/points.json'
            ).json()
            return response["alfreds"]
        except:
            return []  


    def historical_driver_available(self, validate_data):
        """
        Se consultan los historicos para validar si estan disponibles los conductores en ese horario o alguno en su trayectoria esta mas cerca
        """
        driver_not_available = []
        drivers_scheduled_at_previous_times = {}

        # Se consultan las reservaciónes del mismo dia con horario anterior y las del mismo horario
        instance_driver_available = DriverAvailableModel.objects.filter(
            Q(schedule=validate_data["driver_available"]["schedule"])|
            Q(
                schedule__year=validate_data["driver_available"]["schedule"].year,
                schedule__day=validate_data["driver_available"]["schedule"].day,
                schedule__day__gt=validate_data["driver_available"]["schedule"].hour
            )
        )

        # Se compara las reservas para el conductor para la hora actual para excluirlo 
        # Si existe el registro en bd lo que se hace es actualizar la api consumida 
        for driver in instance_driver_available:            
            if driver.schedule == validate_data["driver_available"]["schedule"]:
                driver_not_available.append(driver.driver)
            else:
                drivers_scheduled_at_previous_times["driver"] = {
                    "id": driver.id,
                    "lat": driver.delivery_latitude, 
                    "lng": driver.delivery_longitude
                }           
                        
        return driver_not_available, drivers_scheduled_at_previous_times

    def find_the_nearest_driver(self, validate_data):
        """
        Se busca el conductor mas cercano y se asigna la entrega
        """         
        nearest_driver_available = {}
        nearest_coordinates = None
        
        driver_not_available, drivers_scheduled_at_previous_times = self.historical_driver_available(validate_data)
        for driver in self.get_list_drivers():
            if not str(driver["id"]) in driver_not_available:
                if driver["id"] in drivers_scheduled_at_previous_times:
                    driver = drivers_scheduled_at_previous_times[driver["id"]]
                    
                current_coordinates = dist(
                    (int(driver["lat"]), int(driver["lng"])), 
                    (validate_data["pickup_latitude"], validate_data["pickup_longitude"])   
                )
                
                if not nearest_coordinates or nearest_coordinates > current_coordinates:
                    nearest_coordinates = current_coordinates
                    nearest_driver_available = driver["id"]
        return nearest_driver_available
    
    def create(self, validated_data):
        """
        Se sobreescribe función para la creación de ordenes y asignarlas
        """
        nearest_driver_id = self.find_the_nearest_driver(validated_data)
                
        if not nearest_driver_id:
            raise serializers.ValidationError("No contamos con conductores disponibles en este horario")
        
        instance_driver_available = DriverAvailableModel.objects.create(
            **validated_data["driver_available"],            
            driver=nearest_driver_id
        )
        
        validated_data.pop('driver_available')
        instance = OrderModel.objects.create(**validated_data, driver_available=instance_driver_available)
        return instance

    class Meta:
        model = OrderModel
        fields = "__all__"


class NearestDriverSerializer(serializers.Serializer):
    driver_available__schedule = serializers.DateTimeField()
    driver_available__delivery_latitude = serializers.IntegerField(min_value=0, max_value=100)
    driver_available__delivery_longitude = serializers.IntegerField(min_value=0, max_value=100)