from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transport.models import OrderModel

class AccountTests(APITestCase):
    
    def initial_data(self):
        return {
            "driver_available": {
                "schedule": "2022-10-02T15:36:27.098Z",
                "delivery_latitude": 100,
                "delivery_longitude": 100
            },
            "pickup_latitude": 100,
            "pickup_longitude": 100
        }
        
    def test_date_format(self):
        """
        Test para probar si el formato de fecha es valido
        """
        data = self.initial_data()
        data["driver_available"]["schedule"] = "2022-10-02T15:36:27.098Z"
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["driver_available"]["schedule"][0].title(), 
            'Fecha/Hora Con Formato Erróneo. Use Uno De Los Siguientes Formatos En Su Lugar: Yyyy-Mm-Dd Hh:Mm.'
        )
        
    def test_creating_order_with_minutes(self):
        """
        Test para probar si la fecha contiene minutos
        """
        data = self.initial_data()
        data["driver_available"]["schedule"] = "2022-10-02 15:36"
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["driver_available"]["schedule"][0].title(), 
            'La Fecha De Entrega Debe Ser En Horas Exactas'
        )
        
    def test_creating_order_correct(self):
        """
        Test para probar la creación de la orden con un formato correcto
        """
        data = self.initial_data()
        data["driver_available"]["schedule"] = "2022-10-02 15:00"
        url = reverse('order-list')        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderModel.objects.count(), 1)
    
    def test_creating_with_empty_data(self):
        """
        Test para probar la creación de la orden con un json vacio
        """
        url = reverse('order-list')        
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)        
        self.assertEqual(response.data['driver_available'][0].title(), 'Este Campo Es Requerido.')
        self.assertEqual(response.data['pickup_latitude'][0].title(), 'Este Campo Es Requerido.')
        self.assertEqual(response.data['pickup_longitude'][0].title(), 'Este Campo Es Requerido.')

            
    def test_creating_latitud_and_longitude_out_of_range(self):
        """
        Test para probar con latitud y longitud fuera de rango
        """
        data = {
            "driver_available": {
                "schedule": "2022-10-02 15:00",
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
    
    