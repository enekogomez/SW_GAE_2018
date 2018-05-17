# SW_GAE_2018
Proyecto GAE Sistemas Web 2018

Edgar Andrés Santamaría

Eneko Gómez Ferreira




# OBJETIVO

 El objetivo del proyecto es desarrollar una aplicación desplegada en Google App Engine que permita usuario identificarse en eGela y administrar sus tareas pendientes.
 
 # Arquitectura
 
  El proyecto consta de diferentes modelos cada uno dedicados a un fin específico.  Los módulos son los siguientes:
  
 1-  El módulo esquela es el que se encarga de que un usuario pueda Iniciar sesión en la plataforma eGela y obtener las asignaturas y cada una de las tareas pendientes para cada una de ellas.
 2- El módulo GITManager: Se encarga de que el usuario pueda establecer conexión con su cuenta en la plataforma y sea capaz de subir los ficheros generados para una tarea en concreto.
 3- Calendar: Es un modelo encargado de compartir las fechas y ubicaciones de las entregas con la propia aplicación de Google calendar
 
 
 # OBJETOS
 Presente apartado tiene como de escribir de los objetos que conformarán la aplicación.
 
 Objeto user: Es aquel que se encarga de gestionar la información relativa al usuario: ya sea de la información de inicio de sesión para las diferentes plataformas o incluso asignaturas y fechas de las entregas. Este objeto en sí contenido una lista de tareas de ciudad del objeto lista de tareas la cual estará conformada por una colección de tareas que sopesar un objeto con la información de las tareas.
 
 Objeto
