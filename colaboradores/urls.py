from django.urls import path
from . import views

app_name = 'colaboradores'

urlpatterns = [
    path('', views.lista_colaboradores, name='lista_colaboradores'),
    path('agregar/', views.agregar_colaborador, name='agregar_colaborador'),
    path('modificar/<int:pk>/', views.modificar_colaborador, name='modificar_colaborador'),
    path('baja/<int:pk>/', views.dar_baja_colaborador, name='dar_baja_colaborador'),
    path('eliminar/<int:pk>/', views.eliminar_colaborador, name='eliminar_colaborador'),
    path('buscar/', views.buscar_colaborador, name='buscar_colaborador'),
]