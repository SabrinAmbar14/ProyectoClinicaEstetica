from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.helpers import is_admin_user, has_any_role, registrar_accion
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from clientes.models import Cliente
from .models import Servicio, Cita, ProductoConsumido
from .forms import ServicioForm, CitaForm, ProductoConsumidoForm, CalcularServicioForm, BuscarServicioForm
from inventario.models import MovimientoInventario
from .forms import RegistrarServiciosMultipleForm
from colaboradores.models import Colaborador

@login_required
def lista_servicios(request):
    """Lista todos los servicios"""
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'administrador')
    if is_admin:
        servicios = Servicio.objects.all()
    else:
        servicios = Servicio.objects.filter(estado='activo')
    
    context = {
        'servicios': servicios,
    }
    return render(request, 'servicios/listaServicios.html', context)

@login_required
@user_passes_test(is_admin_user)
def agregar_servicio(request):
    """Vista para agregar un nuevo servicio"""
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save()
            messages.success(request, 'Servicio agregado exitosamente.')
            return redirect('servicios:lista_servicios')
    else:
        form = ServicioForm()
    
    context = {
        'form': form,
    }
    return render(request, 'servicios/formularioServicio.html', context)

@login_required
@user_passes_test(is_admin_user)
def modificar_servicio(request, pk):
    """Vista para modificar un servicio existente"""
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado exitosamente.')
            return redirect('servicios:lista_servicios')
    else:
        form = ServicioForm(instance=servicio)
    
    context = {
        'form': form,
        'servicio': servicio,
    }
    return render(request, 'servicios/formularioServicio.html', context)

@login_required
@user_passes_test(is_admin_user)
def dar_baja_servicio(request, pk):
    """Vista para dar de baja un servicio"""
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':
        servicio.estado = 'inactivo'
        servicio.save()
        messages.success(request, 'Servicio dado de baja exitosamente.')
        return redirect('servicios:lista_servicios')
    
    context = {
        'servicio': servicio,
    }
    return render(request, 'servicios/listaServicios.html', context)


@login_required
@user_passes_test(is_admin_user)
def eliminar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        if servicio.estado != 'activo':
            servicio.delete()
            messages.success(request, 'Servicio eliminado correctamente.')
            registrar_accion(request.user, 'eliminar_servicio', modelo='Servicio', objeto_id=pk,
                             descripcion=f"Servicio {servicio.nombre} eliminado")
        else:
            messages.error(request, 'No se puede eliminar un servicio activo. Primero desactívelo.')
        return redirect('servicios:lista_servicios')
    return render(request, 'servicios/listaServicios.html', {'servicio': servicio})

@login_required
def calcular_servicio(request):
    """Vista para calcular el costo de un servicio"""
    form = CalcularServicioForm(request.POST or None)
    total = 0
    descuento = 0
    es_cumpleanos = False
    
    if request.method == 'POST' and form.is_valid():
        cliente = form.cleaned_data['cliente']
        servicio = form.cleaned_data['servicio']
        fecha_cita = form.cleaned_data.get('fecha_cita')
        productos_seleccionados = form.cleaned_data['productos']
        
        # Calcular total base
        total = servicio.precio_base
        
        # Verificar si la fecha de la cita coincide con el cumpleaños del cliente
        # Usar la fecha de la cita si se proporcionó, en caso contrario usar hoy
        fecha_referencia = fecha_cita or timezone.now().date()
        # Normalizar si la fecha_referencia viene como datetime
        if hasattr(fecha_referencia, 'date'):
            fecha_referencia = fecha_referencia.date()

        if cliente.fecha_nacimiento:
            try:
                cumple_mes = cliente.fecha_nacimiento.month
                cumple_dia = cliente.fecha_nacimiento.day
                if (fecha_referencia.month == cumple_mes and fecha_referencia.day == cumple_dia):
                    es_cumpleanos = True
                    # usar Decimal para evitar mezclar Decimal y float
                    descuento = (Decimal(total) * Decimal('0.20')) if total is not None else Decimal('0')
                    total = Decimal(total) - descuento if total is not None else Decimal('0')
            except Exception:
                # proteger contra valores inesperados en fecha_nacimiento
                es_cumpleanos = False
                descuento = Decimal('0')
        
        # Agregar costo de productos
        for producto in productos_seleccionados:
            total += producto.precio_venta
    
    context = {
        'form': form,
        'total': total,
        'descuento': descuento,
        'es_cumpleanos': es_cumpleanos,
        'servicio_obj': servicio if request.method == 'POST' and form.is_valid() else None,
        'productos_objs': list(productos_seleccionados) if request.method == 'POST' and form.is_valid() else [],
    }
    return render(request, 'servicios/calcularServicio.html', context)

@login_required
@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'estilista', 'recepcionista']))
def registrar_servicio(request):
    """Vista para registrar un servicio completado"""
    if request.method == 'POST':
        form_cita = CitaForm(request.POST)
        if form_cita.is_valid():
            cita = form_cita.save(commit=False)
            cita.estado = 'completada'
            cita.duracion_real_minutos = cita.servicio.duracion_minutos
            cita.calcular_precio_final()
            cita.save()
            
            messages.success(request, 'Servicio registrado exitosamente.')
            return redirect('servicios:lista_citas')
    else:
        form_cita = CitaForm()
    
    context = {
        'form_cita': form_cita,
    }
    return render(request, 'servicios/registrarServicio.html', context)


@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'estilista', 'recepcionista']))
def registrar_servicios_multiple(request):
    """Registrar múltiples servicios para un mismo cliente en una sola acción.

    Crea una `Cita` por cada servicio seleccionado. Asociará el estilista desde
    `request.user.colaborador` cuando exista; si no, intentará asignar el primer
    colaborador con cargo 'estilista' (sólo como fallback).
    """
    if request.method == 'POST':
        form = RegistrarServiciosMultipleForm(request.POST)
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            servicios_sel = form.cleaned_data['servicios']
            fecha_cita = form.cleaned_data['fecha_cita']
            observaciones = form.cleaned_data.get('observaciones', '')

            # Determinar estilista (preferir el colaborador asociado al usuario)
            colaborador = getattr(request.user, 'colaborador', None)
            if not colaborador:
                colaborador = Colaborador.objects.filter(cargo='estilista', estado='activo').first()

            citas_creadas = []
            for servicio in servicios_sel:
                cita = Cita(
                    cliente=cliente,
                    servicio=servicio,
                    estilista=colaborador,
                    fecha_cita=fecha_cita,
                    observaciones=observaciones,
                    estado='completada'
                )
                # calcular precio y guardar
                try:
                    cita.calcular_precio_final()
                except Exception:
                    pass
                cita.save()
                citas_creadas.append(cita)

            messages.success(request, f'Se registraron {len(citas_creadas)} servicios para el cliente {cliente}.')
            return render(request, 'servicios/registrarServiciosResumen.html', {'citas': citas_creadas})
    else:
        form = RegistrarServiciosMultipleForm()

    return render(request, 'servicios/registrarServiciosMultiple.html', {'form': form})

@login_required
def lista_citas(request):
    """Lista todas las citas"""
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'administrador')
    role = None
    if hasattr(user, 'perfilusuario'):
        role = user.perfilusuario.rol

    citas = Cita.objects.all().select_related('cliente', 'servicio', 'estilista')
    if not is_admin:
        # Estilistas ven sólo sus citas
        if role == 'estilista':
            colaborador = getattr(user, 'colaborador', None)
            if colaborador:
                citas = citas.filter(estilista=colaborador)
            else:
                citas = Cita.objects.none()
        # Recepcionistas ven citas próximas (desde hoy)
        elif role == 'recepcionista':
            from django.utils import timezone
            hoy = timezone.now().date()
            citas = citas.filter(fecha_cita__date__gte=hoy)
        # Nota: el rol 'gerente' fue eliminado; no hay rama especial para gerentes.
    
    # Filtrar por fecha si se proporciona
    fecha_filtro = request.GET.get('fecha')
    if fecha_filtro:
        try:
            fecha = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            citas = citas.filter(fecha_cita__date=fecha)
        except ValueError:
            pass
    
    context = {
        'citas': citas,
        'fecha_filtro': fecha_filtro,
    }
    return render(request, 'servicios/listaCitas.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'estilista']))
def agregar_producto_consumido(request, cita_id):
    """Vista para agregar productos consumidos a una cita"""
    cita = get_object_or_404(Cita, pk=cita_id)
    
    if request.method == 'POST':
        form = ProductoConsumidoForm(request.POST)
        if form.is_valid():
            producto_consumido = form.save(commit=False)
            producto_consumido.cita = cita
            producto_consumido.precio_unitario = producto_consumido.producto.precio_venta

            # Crear movimiento de inventario usando el usuario actual
            from inventario.models import MovimientoInventario
            try:
                MovimientoInventario.objects.create(
                    producto=producto_consumido.producto,
                    tipo_movimiento='salida',
                    cantidad=producto_consumido.cantidad,
                    motivo=f"Consumo en cita #{cita.id}",
                    usuario=request.user
                )
            except Exception:
                # Si por alguna razón falla el movimiento, no detener la operación.
                pass

            # Evitar que el save del modelo vuelva a crear el movimiento.
            producto_consumido.suppress_movimiento = True
            producto_consumido.save()

            # Actualizar el precio final de la cita
            cita.precio_final = (cita.precio_final or 0) + producto_consumido.subtotal
            cita.save()

            messages.success(request, 'Producto agregado al servicio.')
            registrar_accion(request.user, 'agregar_producto_consumido', modelo='ProductoConsumido', objeto_id=producto_consumido.id,
                             descripcion=f"Producto {producto_consumido.producto.nombre} x{producto_consumido.cantidad} agregado a cita {cita.id}")
            return redirect('servicios:detalle_cita', pk=cita.id)
    else:
        form = ProductoConsumidoForm()
    
    context = {
        'form': form,
        'cita': cita,
    }
    return render(request, 'servicios/agregarProductoConsumido.html', context)

@login_required
def detalle_cita(request, pk):
    """Vista para ver el detalle de una cita"""
    cita = get_object_or_404(Cita, pk=pk)
    productos_consumidos = cita.productos_consumidos.all()
    
    context = {
        'cita': cita,
        'productos_consumidos': productos_consumidos,
    }
    return render(request, 'servicios/detalleCita.html', context)

@login_required
def aviso_cumpleanos(request):
    """Vista para mostrar avisos de cumpleaños"""
    hoy = timezone.now().date()
    clientes_cumpleanos = Cliente.objects.filter(
        fecha_nacimiento__month=hoy.month,
        fecha_nacimiento__day=hoy.day,
        estado='activo'
    )
    
    context = {
        'clientes_cumpleanos': clientes_cumpleanos,
        'hoy': hoy,
    }
    return render(request, 'servicios/avisoCumpleanos.html', context)

@login_required
def buscar_servicio(request):
    """Vista para buscar servicios"""
    servicios = None
    form = BuscarServicioForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_busqueda = form.cleaned_data['tipo_busqueda']
        termino = form.cleaned_data['termino_busqueda']
        precio_maximo = form.cleaned_data['precio_maximo']
        
        servicios = Servicio.objects.filter(estado='activo')
        
        if tipo_busqueda == 'nombre':
            servicios = servicios.filter(nombre__icontains=termino)
        elif tipo_busqueda == 'categoria':
            servicios = servicios.filter(categoria__icontains=termino)
        elif tipo_busqueda == 'precio' and precio_maximo:
            servicios = servicios.filter(precio_base__lte=precio_maximo)
    
    context = {
        'form': form,
        'servicios': servicios,
    }
    return render(request, 'servicios/buscarServicio.html', context)