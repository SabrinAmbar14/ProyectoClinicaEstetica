def rol_flags(request):
    """Context processor que expone banderas útiles sobre el rol del usuario.

        Devuelve:
            - is_admin: True si es administrador (o superuser)
            - user_rol: nombre del rol ('administrador','estilista','recepcionista') o None
    """
    user = getattr(request, 'user', None)
    is_admin = False
    user_rol = None

    if user and user.is_authenticated:
        if getattr(user, 'is_superuser', False):
            is_admin = True
            user_rol = 'administrador'
        else:
            perfil = getattr(user, 'perfilusuario', None)
            if perfil:
                user_rol = perfil.rol
                is_admin = (perfil.rol == 'administrador')

    return {
        'is_admin': is_admin,
        'user_rol': user_rol,
    }
