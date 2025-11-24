from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone

class Cliente(models.Model):
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
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    direccion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES, 
        default='activo'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre', 'apellido']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"
    
    @property
    def es_cumpleanos_hoy(self):
        hoy = timezone.now().date()
        return hoy.month == self.fecha_nacimiento.month and hoy.day == self.fecha_nacimiento.day
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"