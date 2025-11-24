from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.helpers import is_admin_user, has_any_role
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm, BuscarClienteForm
from usuarios.helpers import registrar_accion, is_admin_user, is_estilista_user
from django.utils.http import urlencode
from django.contrib.auth.decorators import user_passes_test

@login_required
def lista_clientes(request):
    # Admin ve todos; otros roles ven solo clientes activos
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'administrador')
    if is_admin:
        clientes = Cliente.objects.all()
    else:
        clientes = Cliente.objects.filter(estado='activo')
    
    context = {
        'clientes': clientes,
    }
    return render(request, 'clientes/listaCliente.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista']))
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente agregado exitosamente.')
            return redirect('clientes:lista_clientes')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
    }
    return render(request, 'clientes/formularioCliente.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista']))
def modificar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('clientes:lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
    }
    return render(request, 'clientes/formularioCliente.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista']))
def dar_baja_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.estado = 'inactivo'
        cliente.save()
        messages.success(request, 'Cliente dado de baja exitosamente.')
        return redirect('clientes:lista_clientes')
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'clientes/listaClientes.html', context)


@login_required
@user_passes_test(is_admin_user)
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        if cliente.estado != 'activo':
            cliente.delete()
            messages.success(request, 'Cliente eliminado correctamente.')
            registrar_accion(request.user, 'eliminar_cliente', modelo='Cliente', objeto_id=pk,
                             descripcion=f"Cliente {cliente.rut} eliminado")
        else:
            messages.error(request, 'No se puede eliminar un cliente activo. Primero desactívelo.')
        return redirect('clientes:lista_clientes')
    return render(request, 'clientes/listaCliente.html', {'cliente': cliente})


@login_required
@user_passes_test(is_estilista_user)
def estilista_registrar_cliente(request):
    """Permite a un estilista registrar un cliente nuevo (solo creación).

    Acepta un parámetro GET `next` para redirigir de vuelta a la página que inició la creación,
    añadiendo `?cliente=<id>` para facilitar selección posterior.
    """
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            registrar_accion(request.user, 'crear_cliente_estilista', modelo='Cliente', objeto_id=cliente.id,
                             descripcion=f"Cliente {cliente.rut} creado por estilista {request.user.username}")
            if next_url:
                sep = '&' if '?' in next_url else '?'
                return redirect(f"{next_url}{sep}cliente={cliente.id}")
            messages.success(request, 'Cliente registrado correctamente.')
            return redirect('usuarios:dashboard_estilista')
    else:
        form = ClienteForm()

    context = {
        'form': form,
        'next': next_url,
    }
    return render(request, 'clientes/formularioClienteEstilista.html', context)

@login_required
def buscar_cliente(request):
    clientes = None
    form = BuscarClienteForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_busqueda = form.cleaned_data['tipo_busqueda']
        termino = form.cleaned_data['termino_busqueda']
        
        if tipo_busqueda == 'nombre':
            clientes = Cliente.objects.filter(
                Q(nombre__icontains=termino) | Q(apellido__icontains=termino)
            )
        elif tipo_busqueda == 'rut':
            clientes = Cliente.objects.filter(rut__icontains=termino)
        elif tipo_busqueda == 'telefono':
            clientes = Cliente.objects.filter(telefono__icontains=termino)
    
    context = {
        'form': form,
        'clientes': clientes,
    }
    return render(request, 'clientes/buscarCliente.html', context)