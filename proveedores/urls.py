from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('agregar/', views.agregar_proveedor, name='agregar_proveedor'),
    path('modificar/<int:pk>/', views.modificar_proveedor, name='modificar_proveedor'),
    path('baja/<int:pk>/', views.dar_baja_proveedor, name='dar_baja_proveedor'),
        path('eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('buscar/', views.buscar_proveedor, name='buscar_proveedor'),
    path('detalle/<int:pk>/', views.detalle_proveedor, name='detalle_proveedor'),
]