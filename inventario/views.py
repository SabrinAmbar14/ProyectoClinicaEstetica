from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.helpers import is_admin_user, has_any_role
from django.db.models import Q, F
from .models import Producto, MovimientoInventario
from .forms import ProductoForm, MovimientoInventarioForm, ActualizarStockForm, BuscarProductoForm
from usuarios.helpers import registrar_accion

@login_required
def lista_productos(request):
    """Lista todos los productos"""
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'administrador')

    if is_admin:
        productos = Producto.objects.all()
    else:
        productos = Producto.objects.filter(estado='activo')
    
    productos_bajo_minimo = productos.filter(stock_actual__lte=F('stock_minimo'))

    context = {
        'productos': productos,
        'productos_bajo_minimo_count': productos_bajo_minimo.count(),
    }
    return render(request, 'inventario/listaProductos.html', context)


@login_required
@user_passes_test(is_admin_user)
def agregar_producto(request):
    """Vista para agregar un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado exitosamente.')
            return redirect('inventario:lista_productos')
    else:
        form = ProductoForm()
    
    context = {'form': form}
    return render(request, 'inventario/formularioProducto.html', context)


@login_required
@user_passes_test(is_admin_user)
def modificar_producto(request, pk):
    """Vista para modificar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('inventario:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
    }
    return render(request, 'inventario/formularioProducto.html', context)


@login_required
@user_passes_test(is_admin_user)
def dar_baja_producto(request, pk):
    """Vista para dar de baja un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.estado = 'inactivo'
        producto.save()
        messages.success(request, 'Producto dado de baja exitosamente.')
        return redirect('inventario:lista_productos')
    
    context = {'producto': producto}
    return render(request, 'inventario/listaProductos.html', context)


@login_required
@user_passes_test(is_admin_user)
def actualizar_stock(request, pk):
    """Vista para actualizar stock de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ActualizarStockForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            motivo = form.cleaned_data['motivo']
            
            MovimientoInventario.objects.create(
                producto=producto,
                tipo_movimiento='entrada',
                cantidad=cantidad,
                motivo=motivo,
                usuario=request.user
            )
            
            messages.success(request, f'Stock actualizado: +{cantidad} unidades.')
            return redirect('inventario:lista_productos')
    else:
        form = ActualizarStockForm()
    
    context = {
        'form': form,
        'producto': producto,
    }
    return render(request, 'inventario/actualizarStock.html', context)


@login_required
def bajo_minimos(request):
    """Lista productos bajo stock mínimo"""
    productos_bajo_minimo = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        estado='activo'
    )
    
    context = {'productos': productos_bajo_minimo}
    return render(request, 'inventario/bajoMinimos.html', context)


@login_required
def buscar_producto(request):
    """Vista para buscar productos"""
    productos = None
    form = BuscarProductoForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_busqueda = form.cleaned_data['tipo_busqueda']
        termino = form.cleaned_data['termino_busqueda']
        
        if tipo_busqueda == 'nombre':
            productos = Producto.objects.filter(nombre__icontains=termino)
        elif tipo_busqueda == 'categoria':
            productos = Producto.objects.filter(categoria__icontains=termino)
        elif tipo_busqueda == 'bajo_minimo':
            productos = Producto.objects.filter(
                stock_actual__lte=F('stock_minimo'),
                estado='activo'
            )
    
    context = {
        'form': form,
        'productos': productos,
    }
    return render(request, 'inventario/buscarProducto.html', context)


@login_required
@user_passes_test(is_admin_user)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        if producto.estado != 'activo':
            producto.delete()
            messages.success(request, 'Producto eliminado correctamente.')
            registrar_accion(request.user, 'eliminar_producto', modelo='Producto', objeto_id=pk,
                             descripcion=f"Producto {producto.nombre} eliminado")
        else:
            messages.error(request, 'No se puede eliminar un producto activo. Primero desactívelo.')
        return redirect('inventario:lista_productos')
    
    return render(request, 'inventario/listaProductos.html', {'producto': producto})
