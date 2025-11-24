from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Colaborador(models.Model):
    CARGO_CHOICES = [
        ('estilista', 'Estilista'),
        ('recepcionista', 'Recepcionista'),
        ('administrador', 'Administrador'),
    ]
    
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
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    fecha_contratacion = models.DateField()
    sueldo = models.DecimalField(max_digits=10, decimal_places=2)
    direccion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='activo'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='colaborador'
    )
    
    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nombre', 'apellido']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.get_cargo_display()}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"