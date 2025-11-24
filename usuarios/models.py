from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class PerfilUsuario(models.Model):
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('estilista', 'Estilista'),
        ('recepcionista', 'Recepcionista'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=15, choices=ROL_CHOICES, default='recepcionista')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    fecha_contratacion = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_rol_display()}"
    
    @property
    def nombre_completo(self):
        return self.usuario.get_full_name()
    
    @property
    def email(self):
        return self.usuario.email


class AccionHistorial(models.Model):
    """Registro simple de acciones importantes en el sistema para auditoría.

    Se usa para que administradores puedan revisar quién hizo qué y cuándo.
    """
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=150)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    objeto_id = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Acción Historial"
        verbose_name_plural = "Historial de Acciones"
        ordering = ['-fecha']

    def __str__(self):
        usuario_repr = self.usuario.username if self.usuario else 'Sistema'
        return f"[{self.fecha.strftime('%Y-%m-%d %H:%M')}] {usuario_repr} - {self.accion}"

# Señal para crear perfil automáticamente cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Si el usuario creado es superuser, asignar rol administrador
        rol_inicial = 'administrador' if instance.is_superuser else 'recepcionista'
        PerfilUsuario.objects.create(usuario=instance, rol=rol_inicial)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    # Guardar perfil si existe (protección contra usuarios sin perfil)
    if hasattr(instance, 'perfilusuario') and instance.perfilusuario is not None:
        instance.perfilusuario.save()