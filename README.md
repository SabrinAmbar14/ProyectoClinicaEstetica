# ProyectoClinicaEstetica
Descripción
Sistema ERP para gestión integral de salones de belleza desarrollado en Django. Controla inventario, clientes, servicios, colaboradores y proveedores.

Instalación Rápida

Prerrequisitos

Python 3.9+
MySQL 8.0+
Git

Instalación

Clonar repositorio

git clone https://github.com/SabrinAmbar14/ProyectoClinicalEstetica.git
cd ProyectoClinicalEstetica

Entorno virtual

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

Instalar dependencias

pip install django pymysql mysqlclient

Configurar MySQL

Crear base de datos: clinica_estetica
Configurar usuario con permisos
Configurar conexión BD
Modificar settings.py para usar MySQL
Configurar credenciales de conexión

Migraciones

python manage.py migrate

Ejecutar servidor

python manage.py runserver

Configuración MySQL

Database Settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clinica_estetica',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
    }
}

Módulos
Gestión de inventario con control de stock
Sistema de clientes y descuentos automáticos
Control de servicios y citas
Dashboard con métricas en tiempo real

Acceso
URL: http://localhost:8000
Usuario demo: admin / admin123
URL: http://localhost:8000

Usuario demo: admin / admin123
