# Servicio para el transporte de productos

**Tecnologias usadas:**
* django-debug-toolbar==3.7.0 (Nos ayuda a verificar las query y performance)
* djangorestframework==3.14.0
* django-filter==22.1 (Filtros adiccionales en el servicio)
* drf-yasg==1.21.4 (Genera documentación en swagger)
* requests==2.28.1 (Consultar servicio externo)

**Instrucciónes para su ejecución**
* Crear entorno virtual python
* Instalar el archivo requeriments.txt 
* Activar el entorno y correr el servicio de django
* En la ruta inicial se encontrara la documentación en swagger

**Funcionalidades:**
* Agendar un pedido a un conductor en una fecha y hora, y especificar su lugar de recogida (latitud y longitud) y destino. 
* Consultar todos los pedidos asignados en un día en específico ordenados por la hora. 
* Consultar todos los pedidos de un conductor en un día en específico ordenados por la hora. 
* Hacer búsquedas del conductor que esté más cerca de un punto geográfico en una fecha y hora. (Tener en consideración los pedidos ya asignados al conductor). 

**Condiciónes:**
* Todo pedido dura 1 hora.
* No se usarán coordenadas reales, Las coordenadas están dadas partiendo de un cuadro de 100 x 100 partiendo de la coordenada 0,0 hasta la 100,100 

**Notas**  
Es muy extenso lo que se puede realizar con este desarrollo entonces algunas caracteristicas no estaran disponibles como las siguientes:
* Update: si se actualiza el destino me faltaria clarificarlo ya que se puede reasignar otro conductor que podria estar mas cerca a la ruta de entrega adicionalmente habria que definir un tiempo de actualización ya que no se puede actualizar un pedido que se encuentra en camino
* La eliminación estara disponible pero tambien seria prudente definir una hora maxima de eliminación se deja activa para pruebas
