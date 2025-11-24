from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.helpers import is_admin_user, has_any_role
from django.db.models import Q
from .models import Proveedor
from .forms import ProveedorForm, BuscarProveedorForm
from usuarios.helpers import registrar_accion
from django.contrib.auth.decorators import user_passes_test

@login_required
def lista_proveedores(request):
    """Lista todos los proveedores"""
    proveedores = Proveedor.objects.all()
    
    context = {
        'proveedores': proveedores,
    }
    return render(request, 'proveedores/listaProveedores.html', context)

@login_required
@user_passes_test(is_admin_user)
def agregar_proveedor(request):
    """Vista para agregar un nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, 'Proveedor agregado exitosamente.')
            return redirect('proveedores:lista_proveedores')
    else:
        form = ProveedorForm()
    
    context = {
        'form': form,
    }
    return render(request, 'proveedores/formularioProveedor.html', context)

@login_required
@user_passes_test(is_admin_user)
def modificar_proveedor(request, pk):
    """Vista para modificar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
            return redirect('proveedores:lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor,
    }
    return render(request, 'proveedores/formularioProveedor.html', context)

@login_required
@user_passes_test(is_admin_user)
def dar_baja_proveedor(request, pk):
    """Vista para dar de baja un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        proveedor.estado = 'inactivo'
        proveedor.save()
        messages.success(request, 'Proveedor dado de baja exitosamente.')
        return redirect('proveedores:lista_proveedores')
    
    context = {
        'proveedor': proveedor,
    }
    return render(request, 'proveedores/listaProveedores.html', context)


@login_required
@user_passes_test(is_admin_user)
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        if proveedor.estado != 'activo':
            proveedor.delete()
            messages.success(request, 'Proveedor eliminado correctamente.')
            registrar_accion(request.user, 'eliminar_proveedor', modelo='Proveedor', objeto_id=pk,
                             descripcion=f"Proveedor {proveedor.nombre_empresa} eliminado")
        else:
            messages.error(request, 'No se puede eliminar un proveedor activo. Primero desactívelo.')
        return redirect('proveedores:lista_proveedores')
    return render(request, 'proveedores/listaProveedores.html', {'proveedor': proveedor})

@login_required
def buscar_proveedor(request):
    """Vista para buscar proveedores"""
    proveedores = None
    form = BuscarProveedorForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_busqueda = form.cleaned_data['tipo_busqueda']
        termino = form.cleaned_data['termino_busqueda']
        
        if tipo_busqueda == 'empresa':
            proveedores = Proveedor.objects.filter(nombre_empresa__icontains=termino)
        elif tipo_busqueda == 'contacto':
            proveedores = Proveedor.objects.filter(nombre_contacto__icontains=termino)
        elif tipo_busqueda == 'rut':
            proveedores = Proveedor.objects.filter(rut__icontains=termino)
    
    context = {
        'form': form,
        'proveedores': proveedores,
    }
    return render(request, 'proveedores/buscarProveedor.html', context)

@login_required
def detalle_proveedor(request, pk):
    """Vista para ver el detalle de un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    # Obtener productos asociados a este proveedor
    from inventario.models import Producto
    productos_asociados = Producto.objects.filter(proveedor=proveedor, estado='activo')
    
    context = {
        'proveedor': proveedor,
        'productos_asociados': productos_asociados,
    }
    return render(request, 'proveedores/detalleProveedor.html', context)