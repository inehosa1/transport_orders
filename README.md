# Servicio para el transporte de productos

**Tecnologias usadas:**
* Django Debug Toolbar (Nos ayuda a verificar las query y performance)
* djangorestframework==3.14.0
* django-filter==22.1 (Filtros adiccionales en el servicio)
* drf-yasg==1.21.4 (Genera documentación en swagger)
* requests==2.28.1 (Consultar servicio externo)

**Instrucciónes para su ejecución**
* Crear entorno virtual python
* Instalar el archivo requeriments.txt 
* Activar el entorno y correr el servicio de django

**Funcionalidades:**
* Agendar un pedido a un conductor en una fecha y hora, y especificar su lugar de recogida (latitud y longitud) y destino. 
* Consultar todos los pedidos asignados en un día en específico ordenados por la hora. 
* Consultar todos los pedidos de un conductor en un día en específico ordenados por la hora. 
* Hacer búsquedas del conductor que esté más cerca de un punto geográfico en una fecha y hora. (Tener en consideración los pedidos ya asignados al conductor). 

**Condiciónes:**
* Todo pedido dura 1 hora.
* No se usarán coordenadas reales, Las coordenadas están dadas partiendo de un cuadro de 100 x 100 partiendo de la coordenada 0,0 hasta la 100,100 
