from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('modificar/<int:pk>/', views.modificar_cliente, name='modificar_cliente'),
    path('baja/<int:pk>/', views.dar_baja_cliente, name='dar_baja_cliente'),
    path('eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('estilista/registrar/', views.estilista_registrar_cliente, name='estilista_registrar_cliente'),
    path('buscar/', views.buscar_cliente, name='buscar_cliente'),
]