from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('champu', 'Champú'),
        ('acondicionador', 'Acondicionador'),
        ('tinte', 'Tinte'),
        ('laca', 'Laca'),
        ('crema', 'Crema'),
        ('tratamiento', 'Tratamiento'),
        ('otros', 'Otros'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock_actual})"
    
    @property
    def esta_bajo_minimo(self):
        return self.stock_actual <= self.stock_minimo
    
    @property
    def margen_ganancia(self):
        if self.precio_costo > 0:
            return ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
        return 0

    @property
    def diferencia_minima(self):
        """Cantidad necesaria para llegar al stock mínimo (positivo si falta)."""
        try:
            diff = self.stock_minimo - self.stock_actual
            return diff if diff > 0 else 0
        except Exception:
            return 0

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=200)
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.nombre} - {self.cantidad}"
    
    def save(self, *args, **kwargs):
        if self.tipo_movimiento == 'entrada':
            self.producto.stock_actual += self.cantidad
        elif self.tipo_movimiento == 'salida':
            self.producto.stock_actual -= self.cantidad
        self.producto.save()
        super().save(*args, **kwargs)