from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('listaUsuarios', views.lista_usuarios, name='lista_usuarios'),
    path('agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('modificar/<int:pk>/', views.modificar_usuario, name='modificar_usuario'),
    path('desactivar/<int:pk>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('activar/<int:pk>/', views.activar_usuario, name='activar_usuario'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('buscar/', views.buscar_usuario, name='buscar_usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # URLs de autenticación de Django
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Vistas por rol
    path('dashboard/estilista/', views.dashboard_estilista, name='dashboard_estilista'),
    path('estilista/buscar-clientes/', views.estilista_buscar_clientes, name='estilista_buscar_clientes'),
    path('estilista/registrar-servicio/', views.estilista_registrar_servicio, name='estilista_registrar_servicio'),
    path('estilista/agendar-cita/', views.estilista_agendar_cita, name='estilista_agendar_cita'),
    path('estilista/inventario/', views.estilista_ver_inventario, name='estilista_inventario'),

    path('dashboard/recepcionista/', views.dashboard_recepcionista, name='dashboard_recepcionista'),
    path('recepcionista/clientes/', views.recepcionista_gestion_clientes, name='recepcionista_gestion_clientes'),
    # Registro (solo administradores)
    path('register/', views.register_user, name='register'),
    # El rol 'gerente' ya no existe; ruta eliminada
]