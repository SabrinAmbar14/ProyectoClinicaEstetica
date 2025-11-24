from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.reportes_principal, name='reportes_principal'),
    path('inventario/', views.reporte_inventario, name='reporte_inventario'),
    path('clientes/', views.reporte_clientes, name='reporte_clientes'),
    path('productos-mas-vendidos/', views.reporte_productos_mas_vendidos, name='reporte_productos_mas_vendidos'),
    path('stock-bajo/', views.reporte_stock_bajo, name='reporte_stock_bajo'),
    path('historial/', views.historial_reportes, name='historial_reportes'),
    path('exportar/inventario/csv/', views.exportar_inventario_csv, name='exportar_inventario_csv'),
    path('exportar/inventario/pdf/', views.exportar_inventario_pdf, name='exportar_inventario_pdf'),
]