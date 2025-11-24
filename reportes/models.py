from django.db import models
from django.core.validators import MinValueValidator

class Reporte(models.Model):
    TIPO_REPORTE_CHOICES = [
        ('inventario', 'Reporte de Inventario'),
        ('ventas', 'Reporte de Ventas'),
        ('clientes', 'Reporte de Clientes'),
        ('productos_mas_vendidos', 'Productos Más Vendidos'),
        ('stock_bajo', 'Productos Bajo Stock Mínimo'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo_reporte = models.CharField(max_length=30, choices=TIPO_REPORTE_CHOICES)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    parametros = models.JSONField(default=dict, blank=True)  # Para guardar filtros usados
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_reporte_display()}"

# No necesitamos más modelos para reportes básicos
# Los reportes se generarán dinámicamente desde las vistas