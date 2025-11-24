from django.db import models
from django.core.validators import MinLengthValidator

class Proveedor(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[MinLengthValidator(9)],
        help_text="Formato: 12345678-9"
    )
    nombre_empresa = models.CharField(max_length=100)
    nombre_contacto = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    productos_que_suministra = models.TextField(help_text="Lista de productos que provee")
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='activo'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre_empresa']
    
    def __str__(self):
        return f"{self.nombre_empresa} - {self.nombre_contacto}"
    
    @property
    def cantidad_productos(self):
        """Retorna la cantidad de productos asociados a este proveedor"""
        from inventario.models import Producto
        return Producto.objects.filter(proveedor=self, estado='activo').count()