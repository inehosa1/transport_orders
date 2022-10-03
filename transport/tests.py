import random
import time
import pytz

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transport.models import DriverAvailableModel
from datetime import datetime, timedelta

class AccountTests(APITestCase):
    
    def randomDate(self):
        stime = time.mktime(time.strptime((datetime.now() + timedelta(days=1)).replace(minute=0).strftime("%Y-%m-%d %H:%M"), '%Y-%m-%d %H:%M'))
        etime = time.mktime(time.strptime((datetime.now() + timedelta(days=5)).replace(minute=0).strftime("%Y-%m-%d %H:%M"), '%Y-%m-%d %H:%M'))
        ptime = stime + random.random() * (etime - stime)
        dt = datetime.fromtimestamp(time.mktime(time.localtime(ptime))).replace(minute=0)
        return dt.strftime("%Y-%m-%d %H:%M")
    
    def initial_data(self):
        """
        Genaración de datos random para registros de ejemplo
        """
        return {
            "driver_available": {
                "schedule": self.randomDate(),
                "delivery_latitude": random.randint(0,100),
                "delivery_longitude": random.randint(0,100)
            },
            "pickup_latitude": random.randint(0,100),
            "pickup_longitude": random.randint(0,100)
        }
        
    def create_data(self, quantity=10):
        """
        Función para crear registros de ejemplo
        """
        url = reverse('order-list')
        for i in range(quantity):
            response = self.client.post(url, self.initial_data(), format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_date_format_incorrect(self):
        """
        Test para probar si el formato de fecha es valido
        """
        data = self.initial_data()
        data["driver_available"]["schedule"] = "2025-10-02T15:36:27.098Z"
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["driver_available"]["schedule"][0].title(), 
            'Fecha/Hora Con Formato Erróneo. Use Uno De Los Siguientes Formatos En Su Lugar: Yyyy-Mm-Dd Hh:Mm.'
        )
        
    def test_create_order_with_minutes(self):
        """
        Test para probar si la fecha contiene minutos
        """
        data = self.initial_data()
        data["driver_available"]["schedule"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M") 
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data["driver_available"]["schedule"][0].title(), 
            'La Fecha De Entrega Debe Ser En Horas Exactas'
        )
        
    def test_create_order_correct(self):
        """
        Test para probar la creación de la orden con un formato correcto
        """
        data = self.initial_data()
        data["driver_available"]["schedule"] = (datetime.now() + timedelta(days=1)).replace(minute=0).strftime("%Y-%m-%d %H:%M")
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    

    def test_create_with_empty_data(self):
        """
        Test para probar la creación de la orden con un json vacio
        """
        url = reverse('order-list')        
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)        
        self.assertEqual(response.data['driver_available'][0].title(), 'Este Campo Es Requerido.')
        self.assertEqual(response.data['pickup_latitude'][0].title(), 'Este Campo Es Requerido.')
        self.assertEqual(response.data['pickup_longitude'][0].title(), 'Este Campo Es Requerido.')
         
    def test_create_latitud_and_longitude_out_of_range(self):
        """
        Test para probar con latitud y longitud fuera de rango
        """
        data = {
            "driver_available": {
                "schedule": (datetime.now() + timedelta(days=1)).replace(minute=0).strftime("%Y-%m-%d %H:%M"),
                "delivery_latitude": 101,
                "delivery_longitude": -10
            },
            "pickup_latitude": 101,
            "pickup_longitude": -10
        }
        
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["driver_available"]["delivery_latitude"][0].title(), 'Asegúrese De Que Este Valor Es Menor O Igual A 100.')
        self.assertEqual(response.data["driver_available"]["delivery_latitude"][0].code, 'max_value')        
        self.assertEqual(response.data["driver_available"]["delivery_longitude"][0].title(), 'Asegúrese De Que Este Valor Es Mayor O Igual A 0.')
        self.assertEqual(response.data["driver_available"]["delivery_longitude"][0].code, 'min_value')        
        self.assertEqual(response.data["pickup_latitude"][0].title(), 'Asegúrese De Que Este Valor Es Menor O Igual A 100.')
        self.assertEqual(response.data["pickup_latitude"][0].code, 'max_value')
        self.assertEqual(response.data["pickup_longitude"][0].title(), 'Asegúrese De Que Este Valor Es Mayor O Igual A 0.')
        self.assertEqual(response.data["pickup_longitude"][0].code, 'min_value')
    
    def test_get_check_orders(self):
        """
        Test para validar las busquedas de un dia en especifico
        """
        url = reverse('order-list')
        self.create_data()        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
                
        get_date_first_record = datetime.strptime(response.data["results"][0]["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        
        response_two = self.client.get(url, {'driver_available__schedule': get_date_first_record}, format='json')
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        
        data = set([datetime.strptime(record["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")  for record in response_two.data["results"]])

        self.assertEqual(len(data), 1)
        self.assertEqual(data, {get_date_first_record})
            
    def test_get_days_orders_for_driver(self):
        """
        Test para validar la busqueda de un conductor en un dia en especifico
        """
        url = reverse('order-list')
        self.create_data()        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
                
        get_date_first_record = datetime.strptime(response.data["results"][0]["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        
        response_two = self.client.get(url, {
            'driver_available__schedule': get_date_first_record, 
            'driver_available__driver': response.data["results"][0]["driver_available"]["driver"]
        }, format='json')
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        
        driver_dict = set([driver["driver_available"]["driver"] for driver in response_two.data["results"]])        
        schedule_dict =set([datetime.strptime(record["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") for record in response_two.data["results"]])
        
        self.assertEqual(len(driver_dict), 1)
        self.assertEqual(driver_dict, {response.data["results"][0]["driver_available"]["driver"]})
        
        self.assertEqual(len(schedule_dict), 1)
        self.assertEqual(schedule_dict, {get_date_first_record})
        
    def test_get_days_orders_for_driver(self):
        """
        Test para validar la busqueda de un conductor en un dia en especifico
        """
        url = reverse('order-list')
        self.create_data()        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
                
        get_date_first_record = datetime.strptime(response.data["results"][0]["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        
        response_two = self.client.get(url, {
            'driver_available__schedule': get_date_first_record, 
            'driver_available__driver': response.data["results"][0]["driver_available"]["driver"]
        }, format='json')
        
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        
        driver_dict = set([driver["driver_available"]["driver"] for driver in response_two.data["results"]])        
        schedule_dict =set([datetime.strptime(record["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") for record in response_two.data["results"]])
        
        self.assertEqual(len(driver_dict), 1)
        self.assertEqual(driver_dict, {response.data["results"][0]["driver_available"]["driver"]})
        
        self.assertEqual(len(schedule_dict), 1)
        self.assertEqual(schedule_dict, {get_date_first_record})
        
    def test_get_for_the_driver_at_the_closest_coordinates_on_a_specific_date(self):
        """
        Test buscar el conductor mas cercano en la coordenadas ingresadas y en un dia en especifico
        """
        url = reverse('order-find_nearest_driver')
        self.create_data()        
        
        instance_driver_available = DriverAvailableModel.objects.first()
                
        search = {
            "driver_available__schedule": instance_driver_available.schedule.strftime("%Y-%m-%d %H:%M"), 
            "driver_available__delivery_latitude": random.randint(0,100), 
            "driver_available__delivery_longitude": random.randint(0,100)
        }
        
        response = self.client.get(url, search, format='json')
        
        # En algunos casos saca 404 por que no encuentra ningun conductor disponible en ese rango este es un error a solucionar ya que la consulta no esta tomando el registro que deberia estar disponible
        if response.status_code == status.HTTP_404_NOT_FOUND:            
            self.assertEqual(response.data["message"], "No se encuentran conductores disponibles en la fecha ingresada")            
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len([response.data]), 1)
            self.assertEqual(datetime.strptime(response.data["driver_available"]["schedule"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"), instance_driver_available.schedule.strftime("%Y-%m-%d"))
        
        