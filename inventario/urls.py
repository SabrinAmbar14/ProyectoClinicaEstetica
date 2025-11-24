from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('modificar/<int:pk>/', views.modificar_producto, name='modificar_producto'),
    path('baja/<int:pk>/', views.dar_baja_producto, name='dar_baja_producto'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('actualizar-stock/<int:pk>/', views.actualizar_stock, name='actualizar_stock'),
    path('bajo-minimos/', views.bajo_minimos, name='bajo_minimos'),
    path('buscar/', views.buscar_producto, name='buscar_producto'),
]