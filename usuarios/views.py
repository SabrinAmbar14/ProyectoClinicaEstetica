from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from .models import PerfilUsuario
from .helpers import registrar_accion
from .forms import (
    RegistroUsuarioForm, PerfilUsuarioForm, EditarUsuarioForm, 
    CambiarPasswordForm, BuscarUsuarioForm
)

def es_administrador(user):
    """Verifica si el usuario es administrador"""
    # Permitir superusuarios (creados con createsuperuser) aunque no tengan PerfilUsuario
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'administrador'


def es_estilista(user):
    """Verifica si el usuario es estilista"""
    return user.is_authenticated and hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'estilista'


def es_recepcionista(user):
    """Verifica si el usuario es recepcionista"""
    return user.is_authenticated and hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'recepcionista'


# El rol 'gerente' fue eliminado del sistema; no se requiere función comprobadora.

@login_required
@user_passes_test(es_administrador)
def lista_usuarios(request):
    """Lista todos los usuarios (solo administradores)"""
    usuarios = User.objects.all().select_related('perfilusuario')
    
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios/listaUsuarios.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_usuario(request):
    """Vista para agregar un nuevo usuario (solo administradores)"""
    if request.method == 'POST':
        form_usuario = RegistroUsuarioForm(request.POST)
        form_perfil = PerfilUsuarioForm(request.POST)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save()
            
            # Asignar el perfil al usuario
            perfil = form_perfil.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            
            messages.success(request, 'Usuario creado exitosamente.')
            registrar_accion(request.user, 'crear_usuario', modelo='User', objeto_id=usuario.id,
                             descripcion=f"Usuario {usuario.username} creado con rol {perfil.rol}")
            return redirect('usuarios:lista_usuarios')
    else:
        form_usuario = RegistroUsuarioForm()
        form_perfil = PerfilUsuarioForm()
    
    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }
    return render(request, 'usuarios/formularioUsuario.html', context)

@login_required
@user_passes_test(es_administrador)
def modificar_usuario(request, pk):
    """Vista para modificar un usuario existente (solo administradores)"""
    usuario = get_object_or_404(User, pk=pk)
    perfil = get_object_or_404(PerfilUsuario, usuario=usuario)
    
    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        form_perfil = PerfilUsuarioForm(request.POST, instance=perfil)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            registrar_accion(request.user, 'modificar_usuario', modelo='User', objeto_id=usuario.id,
                             descripcion=f"Usuario {usuario.username} modificado")
            return redirect('usuarios:lista_usuarios')
    else:
        form_usuario = EditarUsuarioForm(instance=usuario)
        form_perfil = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'usuario': usuario,
    }
    return render(request, 'usuarios/formularioUsuario.html', context)

@login_required
@user_passes_test(es_administrador)
def desactivar_usuario(request, pk):
    """Vista para desactivar un usuario (solo administradores)"""
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()
        messages.success(request, 'Usuario desactivado exitosamente.')
        registrar_accion(request.user, 'desactivar_usuario', modelo='User', objeto_id=usuario.id,
                 descripcion=f"Usuario {usuario.username} desactivado")
        return redirect('usuarios:lista_usuarios')
    
    context = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/listaUsuarios.html', context)

@login_required
@user_passes_test(es_administrador)
def activar_usuario(request, pk):
    """Vista para activar un usuario (solo administradores)"""
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()
        messages.success(request, 'Usuario activado exitosamente.')
        registrar_accion(request.user, 'activar_usuario', modelo='User', objeto_id=usuario.id,
                 descripcion=f"Usuario {usuario.username} activado")
        return redirect('usuarios:lista_usuarios')
    
    context = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/listaUsuarios.html', context)


@login_required
@user_passes_test(es_administrador)
def eliminar_usuario(request, pk):
    """Elimina un usuario del sistema (solo administradores). Solo se permite eliminar usuarios inactivos."""
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if not usuario.is_active:
            usuario.delete()
            messages.success(request, 'Usuario eliminado correctamente.')
            registrar_accion(request.user, 'eliminar_usuario', modelo='User', objeto_id=pk,
                             descripcion=f"Usuario {usuario.username} eliminado")
        else:
            messages.error(request, 'No se puede eliminar un usuario activo. Primero desactívelo.')
        return redirect('usuarios:lista_usuarios')

    context = {'usuario': usuario}
    return render(request, 'usuarios/listaUsuarios.html', context)

@login_required
def mi_perfil(request):
    """Vista para que el usuario vea y edite su propio perfil"""
    perfil = get_object_or_404(PerfilUsuario, usuario=request.user)
    
    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=request.user)
        form_perfil = PerfilUsuarioForm(request.POST, instance=perfil)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:mi_perfil')
    else:
        form_usuario = EditarUsuarioForm(instance=request.user)
        form_perfil = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'perfil': perfil,
    }
    return render(request, 'usuarios/miPerfil.html', context)


@login_required
@user_passes_test(es_estilista)
def dashboard_estilista(request):
    """Dashboard básico para estilistas: servicios del día y alertas"""
    from servicios.models import Cita
    hoy = timezone.now().date()
    # Intentar usar la relación OneToOne (User.colaborador) si existe
    colaborador = getattr(request.user, 'colaborador', None)
    if colaborador:
        citas_hoy = Cita.objects.filter(fecha_cita__date=hoy, estilista=colaborador)
    else:
        citas_hoy = Cita.objects.filter(fecha_cita__date=hoy)

    context = {
        'citas_hoy': citas_hoy,
    }
    return render(request, 'usuarios/dashboard_estilista.html', context)


@login_required
@user_passes_test(es_estilista)
def estilista_buscar_clientes(request):
    """Permite que el estilista busque clientes (solo lectura)"""
    from clientes.models import Cliente
    termino = request.GET.get('q')
    clientes = Cliente.objects.filter(estado='activo')
    if termino:
        clientes = clientes.filter(Q(nombre__icontains=termino) | Q(apellido__icontains=termino) | Q(telefono__icontains=termino))

    context = {'clientes': clientes, 'termino': termino}
    return render(request, 'usuarios/estilista_buscar_clientes.html', context)


@login_required
@user_passes_test(es_estilista)
def estilista_registrar_servicio(request):
    """Vista simple para que el estilista registre servicios (usa el formulario existente)
    Nota: esta vista delega la lógica real a `servicios.registrar_servicio` si se desea.
    """
    from servicios.forms import CitaForm
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            # Asociar el colaborador si la relación User.colaborador existe
            colaborador = getattr(request.user, 'colaborador', None)
            if colaborador:
                cita.estilista = colaborador
            cita.estado = 'completada'
            cita.save()
            messages.success(request, 'Servicio registrado.')
            return redirect('usuarios:dashboard_estilista')
    else:
        form = CitaForm()

    return render(request, 'usuarios/estilista_registrar_servicio.html', {'form': form})


@login_required
@user_passes_test(es_estilista)
def estilista_agendar_cita(request):
    """Permite al estilista agendar (programar) una cita para un cliente.

    Si el cliente no existe, puede usar la vista `clientes:estilista_registrar_cliente` (ya implementada)
    y el flujo devolverá a esta página con `?cliente=<id>` para preseleccionar el cliente.
    """
    from servicios.forms import CitaForm
    # Si llega un parámetro cliente en GET, intentar preseleccionarlo
    cliente_id = request.GET.get('cliente')

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            colaborador = getattr(request.user, 'colaborador', None)
            if colaborador:
                cita.estilista = colaborador
            cita.estado = 'programada'
            cita.save()
            registrar_accion(request.user, 'agendar_cita', modelo='Cita', objeto_id=cita.id,
                             descripcion=f"Cita programada para cliente {cita.cliente.rut} en {cita.fecha_cita}")
            messages.success(request, 'Cita agendada correctamente.')
            return redirect('usuarios:dashboard_estilista')
    else:
        initial = {}
        if cliente_id:
            initial['cliente'] = cliente_id
        form = CitaForm(initial=initial)

    return render(request, 'usuarios/estilista_agendar_cita.html', {'form': form})


@login_required
@user_passes_test(es_estilista)
def estilista_ver_inventario(request):
    """Vista de solo lectura del inventario para estilistas"""
    from inventario.models import Producto
    productos = Producto.objects.filter(estado='activo')
    return render(request, 'usuarios/estilista_inventario.html', {'productos': productos})


@login_required
@user_passes_test(es_recepcionista)
def dashboard_recepcionista(request):
    """Dashboard para recepcionistas: clientes nuevos y cumpleaños"""
    from clientes.models import Cliente
    hoy = timezone.now().date()
    clientes_nuevos = Cliente.objects.filter(fecha_registro__date__gte=(timezone.now() - timedelta(days=7)))[:10]
    cumpleaños_hoy = Cliente.objects.filter(fecha_nacimiento__month=hoy.month, fecha_nacimiento__day=hoy.day, estado='activo')

    context = {
        'clientes_nuevos': clientes_nuevos,
        'cumpleaños_hoy': cumpleaños_hoy,
    }
    return render(request, 'usuarios/dashboard_recepcionista.html', context)


@login_required
@user_passes_test(es_recepcionista)
def recepcionista_gestion_clientes(request):
    """Gestión de clientes para recepcionistas: delega a vistas existentes en app `clientes` si aplica."""
    # Reusar la funcionalidad existente en la app `clientes` si está disponible.
    # Aquí se muestra una vista básica que lista y permite crear/editar mediante enlaces.
    from clientes.models import Cliente
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    return render(request, 'usuarios/recepcionista_gestion_clientes.html', {'clientes': clientes})


# El dashboard de gerente fue eliminado porque el rol ya no existe.

@login_required
def cambiar_password(request):
    """Vista para que el usuario cambie su contraseña"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            password_actual = form.cleaned_data['password_actual']
            nuevo_password = form.cleaned_data['nuevo_password']
            
            # Verificar contraseña actual
            if not request.user.check_password(password_actual):
                messages.error(request, 'La contraseña actual es incorrecta.')
            else:
                request.user.set_password(nuevo_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Contraseña cambiada exitosamente.')
                return redirect('usuarios:mi_perfil')
    else:
        form = CambiarPasswordForm()
    
    context = {
        'form': form,
    }
    return render(request, 'usuarios/cambiarPassword.html', context)

@login_required
@user_passes_test(es_administrador)
def buscar_usuario(request):
    """Vista para buscar usuarios (solo administradores)"""
    usuarios = None
    form = BuscarUsuarioForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_busqueda = form.cleaned_data['tipo_busqueda']
        termino = form.cleaned_data['termino_busqueda']
        
        if tipo_busqueda == 'username':
            usuarios = User.objects.filter(username__icontains=termino)
        elif tipo_busqueda == 'nombre':
            usuarios = User.objects.filter(
                Q(first_name__icontains=termino) | Q(last_name__icontains=termino)
            )
        elif tipo_busqueda == 'email':
            usuarios = User.objects.filter(email__icontains=termino)
        elif tipo_busqueda == 'rol':
            usuarios = User.objects.filter(perfilusuario__rol__icontains=termino)
    
    context = {
        'form': form,
        'usuarios': usuarios,
    }
    return render(request, 'usuarios/buscarUsuario.html', context)

def logout_view(request):
    """Vista personalizada para cerrar sesión"""
    logout(request)
    return render(request, 'registration/logout.html')


@login_required
@user_passes_test(es_administrador)
def register_user(request):
    """Registro de nuevo usuario -- accesible solo para administradores."""
    if request.method == 'POST':
        form_usuario = RegistroUsuarioForm(request.POST)
        if form_usuario.is_valid():
            usuario = form_usuario.save()
            # Obtener rol seleccionado en el formulario (campo 'role')
            role = form_usuario.cleaned_data.get('role', 'recepcionista')
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario, defaults={'rol': role})
            if not created and perfil.rol != role:
                perfil.rol = role
                perfil.save()
            messages.success(request, f"Usuario con RUT '{usuario.username}' registrado correctamente con rol '{perfil.get_rol_display()}'. Ahora puede iniciar sesión con ese RUT.")
            return redirect('usuarios:lista_usuarios')
    else:
        form_usuario = RegistroUsuarioForm()

    context = {
        'form_usuario': form_usuario,
    }
    return render(request, 'registration/register.html', context)