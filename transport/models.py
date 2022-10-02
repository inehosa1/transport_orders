from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class DriverAvailableModel(models.Model):
    """
    Modelo para la asignación de conductores
    """
    driver = models.CharField("Id del conductor", max_length=10)
    schedule = models.DateTimeField("Fecha de entrega")
    delivery_latitude = models.IntegerField("Latitud de entrega", validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
    ])
    delivery_longitude = models.IntegerField("Longitud de entrega", validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
    ])
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=[
                "driver", 
                "schedule"
            ], name="driver_shedule")
        ]
    

class OrderModel(models.Model):
    """
    Modelo para la creación de pedidos
    """
    pickup_latitude = models.IntegerField("Latitud de recogida", validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
    ])
    pickup_longitude = models.IntegerField("Longitud de recogida", validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
    ])
    driver_available = models.ForeignKey(DriverAvailableModel, on_delete=models.CASCADE, verbose_name="order_driver_available")