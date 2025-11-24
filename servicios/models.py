from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Servicio(models.Model):
    CATEGORIA_CHOICES = [
        ('corte', 'Corte'),
        ('tinte', 'Tinte'),
        ('lavado', 'Lavado'),
        ('peinado', 'Peinado'),
        ('manicura', 'Manicura'),
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
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio_base}"

class Cita(models.Model):
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    estilista = models.ForeignKey('colaboradores.Colaborador', on_delete=models.CASCADE, limit_choices_to={'cargo': 'estilista'})
    fecha_cita = models.DateTimeField()
    duracion_real_minutos = models.IntegerField(blank=True, null=True)
    precio_final = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descuento_aplicado = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='programada')
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['-fecha_cita']
    
    def __str__(self):
        return f"{self.cliente.nombre_completo} - {self.servicio.nombre} - {self.fecha_cita.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def es_cumpleanos_cliente(self):
        """Verifica si la cita coincide con el cumpleaños del cliente"""
        return (self.fecha_cita.date().month == self.cliente.fecha_nacimiento.month and 
                self.fecha_cita.date().day == self.cliente.fecha_nacimiento.day)
    
    def calcular_precio_final(self):
        """Calcula el precio final con descuentos aplicados"""
        precio = self.servicio.precio_base
        
        # Aplicar descuento por cumpleaños (20%)
        from decimal import Decimal

        if self.es_cumpleanos_cliente:
            descuento = precio * Decimal('0.20')
            precio -= descuento
            self.descuento_aplicado = descuento

        
        self.precio_final = precio
        return precio
    
    def save(self, *args, **kwargs):
        # Calcular precio final antes de guardar
        if not self.precio_final:
            self.calcular_precio_final()
        super().save(*args, **kwargs)

class ProductoConsumido(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='productos_consumidos')
    producto = models.ForeignKey('inventario.Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Producto Consumido"
        verbose_name_plural = "Productos Consumidos"
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        from django.contrib.auth.models import User
        
        # Actualizar el precio unitario al precio actual del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_venta

        # Por defecto, crear movimiento de salida si no se indica lo contrario.
        suppress = getattr(self, 'suppress_movimiento', False)
        if not suppress:
            # Obtener el primer usuario administrador como usuario por defecto
            usuario_sistema = User.objects.filter(is_superuser=True).first()
            if not usuario_sistema:
                usuario_sistema = User.objects.first()

            if usuario_sistema:
                from inventario.models import MovimientoInventario
                MovimientoInventario.objects.create(
                    producto=self.producto,
                    tipo_movimiento='salida',
                    cantidad=self.cantidad,
                    motivo=f"Consumo en cita #{self.cita.id}",
                    usuario=usuario_sistema
                )

        super().save(*args, **kwargs)