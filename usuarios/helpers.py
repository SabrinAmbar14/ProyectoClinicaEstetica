from django.contrib.auth.models import AnonymousUser
from .models import AccionHistorial


def registrar_accion(usuario, accion, modelo=None, objeto_id=None, descripcion=None):
    """Registra una acción en el historial.

    `usuario` puede ser None (por ejemplo acciones del sistema).
    """
    try:
        AccionHistorial.objects.create(
            usuario=getattr(usuario, 'id', usuario) and usuario,
            accion=accion,
            modelo=modelo,
            objeto_id=str(objeto_id) if objeto_id is not None else None,
            descripcion=descripcion or ''
        )
    except Exception:
        # No queremos que una falla en el logging rompa la operación principal
        pass


def _get_rol(user):
    if not user or isinstance(user, AnonymousUser):
        return None
    if getattr(user, 'is_superuser', False):
        return 'administrador'
    perfil = getattr(user, 'perfilusuario', None)
    if perfil:
        return perfil.rol
    return None


def is_admin_user(user):
    """True si el usuario es administrador o superuser."""
    rol = _get_rol(user)
    return rol == 'administrador'
def has_any_role(user, roles):
    """Comprueba si el usuario tiene alguno de los roles indicados.

    `roles` puede ser una lista o tupla de cadenas.
    """
    rol = _get_rol(user)
    return rol in roles


def is_recepcionista_user(user):
    rol = _get_rol(user)
    return rol in ('recepcionista', 'administrador')


def is_estilista_user(user):
    rol = _get_rol(user)
    return rol in ('estilista', 'administrador')
