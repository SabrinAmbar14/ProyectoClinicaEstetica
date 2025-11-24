from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    path('', views.lista_servicios, name='lista_servicios'),
    path('agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('modificar/<int:pk>/', views.modificar_servicio, name='modificar_servicio'),
    path('baja/<int:pk>/', views.dar_baja_servicio, name='dar_baja_servicio'),
    path('calcular/', views.calcular_servicio, name='calcular_servicio'),
    path('registrar/', views.registrar_servicio, name='registrar_servicio'),
    path('registrar-multiple/', views.registrar_servicios_multiple, name='registrar_servicios_multiple'),
    path('eliminar/<int:pk>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('citas/', views.lista_citas, name='lista_citas'),
    path('citas/<int:pk>/', views.detalle_cita, name='detalle_cita'),
    path('citas/<int:cita_id>/agregar-producto/', views.agregar_producto_consumido, name='agregar_producto_consumido'),
    path('cumpleanos/', views.aviso_cumpleanos, name='aviso_cumpleanos'),
    path('buscar/', views.buscar_servicio, name='buscar_servicio'),
]