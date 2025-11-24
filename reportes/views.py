from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.helpers import has_any_role
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from clientes.models import Cliente
from inventario.models import Producto, MovimientoInventario
from servicios.models import Servicio
from proveedores.models import Proveedor
from .forms import ReporteInventarioForm, ReporteVentasForm, ReporteClientesForm, ReporteProductosForm
from .models import Reporte
from usuarios.helpers import registrar_accion
from django.http import HttpResponse
import csv
import io

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista', 'estilista']))
def reportes_principal(request):
    """Página principal de reportes"""
    # Redirigir a la vista principal de inventario para mostrar las opciones y filtros
    return redirect('reportes:reporte_inventario')

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista', 'estilista']))
def reporte_inventario(request):
    """Genera reportes de inventario"""
    productos = Producto.objects.all()
    form = ReporteInventarioForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_reporte = form.cleaned_data['tipo_reporte']
        categoria = form.cleaned_data['categoria']
        incluir_inactivos = form.cleaned_data['incluir_inactivos']
        
        if not incluir_inactivos:
            productos = productos.filter(estado='activo')
        
        if tipo_reporte == 'bajo_minimo':
            productos = productos.filter(stock_actual__lte=F('stock_minimo'))
        elif tipo_reporte == 'categoria' and categoria:
            productos = productos.filter(categoria=categoria)
        elif tipo_reporte == 'proveedor':
            productos = productos.filter(proveedor__isnull=False)
    
    # Estadísticas
    total_productos = productos.count()
    productos_bajo_minimo = productos.filter(stock_actual__lte=F('stock_minimo')).count()
    valor_total_inventario = sum(p.precio_costo * p.stock_actual for p in productos)
    
    # Guardar el reporte generado
    if request.GET:
        Reporte.objects.create(
            nombre=f"Reporte Inventario - {timezone.now().strftime('%Y-%m-%d')}",
            tipo_reporte='inventario',
            usuario=request.user,
            parametros=form.cleaned_data
        )
    
    context = {
        'form': form,
        'productos': productos,
        'total_productos': total_productos,
        'productos_bajo_minimo': productos_bajo_minimo,
        'valor_total_inventario': valor_total_inventario,
    }
    return render(request, 'reportes/reporteInventario.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista']))
def reporte_clientes(request):
    """Genera reportes de clientes"""
    clientes = Cliente.objects.all()
    form = ReporteClientesForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_reporte = form.cleaned_data['tipo_reporte']
        ordenar_por = form.cleaned_data['ordenar_por']
        
        if tipo_reporte == 'activos':
            clientes = clientes.filter(estado='activo')
        elif tipo_reporte == 'inactivos':
            clientes = clientes.filter(estado='inactivo')
        elif tipo_reporte == 'cumpleanos':
            mes_actual = timezone.now().month
            clientes = clientes.filter(fecha_nacimiento__month=mes_actual)
        
        # Ordenar
        if ordenar_por == 'nombre':
            clientes = clientes.order_by('nombre', 'apellido')
        elif ordenar_por == 'fecha_registro':
            clientes = clientes.order_by('-fecha_registro')
        elif ordenar_por == 'estado':
            clientes = clientes.order_by('estado', 'nombre')
    
    # Estadísticas
    total_clientes = clientes.count()
    clientes_activos = clientes.filter(estado='activo').count()
    clientes_inactivos = clientes.filter(estado='inactivo').count()
    
    context = {
        'form': form,
        'clientes': clientes,
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'clientes_inactivos': clientes_inactivos,
    }
    return render(request, 'reportes/reporteClientes.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista']))
def reporte_productos_mas_vendidos(request):
    """Reporte de productos más vendidos"""
    form = ReporteProductosForm(request.GET or None)
    movimientos = MovimientoInventario.objects.filter(tipo_movimiento='salida')
    
    # Determinar el período
    hoy = timezone.now().date()
    if request.GET and form.is_valid():
        periodo = form.cleaned_data['periodo']
        top_n = form.cleaned_data['top_n']
        
        if periodo == 'hoy':
            fecha_inicio = hoy
            fecha_fin = hoy
        elif periodo == 'semana':
            fecha_inicio = hoy - timedelta(days=hoy.weekday())
            fecha_fin = fecha_inicio + timedelta(days=6)
        elif periodo == 'mes':
            fecha_inicio = hoy.replace(day=1)
            fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif periodo == 'trimestre':
            trimestre_actual = (hoy.month - 1) // 3 + 1
            fecha_inicio = datetime(hoy.year, 3 * (trimestre_actual - 1) + 1, 1).date()
            fecha_fin = (fecha_inicio + timedelta(days=92)).replace(day=1) - timedelta(days=1)
        elif periodo == 'anio':
            fecha_inicio = hoy.replace(month=1, day=1)
            fecha_fin = hoy.replace(month=12, day=31)
        else:  # personalizado
            fecha_inicio = form.cleaned_data['fecha_inicio'] or hoy - timedelta(days=30)
            fecha_fin = form.cleaned_data['fecha_fin'] or hoy
        
        movimientos = movimientos.filter(
            fecha_movimiento__date__range=[fecha_inicio, fecha_fin]
        )
    else:
        # Por defecto: último mes
        fecha_inicio = hoy - timedelta(days=30)
        fecha_fin = hoy
        top_n = 10
        movimientos = movimientos.filter(
            fecha_movimiento__date__range=[fecha_inicio, fecha_fin]
        )
    
    # Agrupar por producto y sumar cantidades
    from django.db.models import Sum
    productos_vendidos = movimientos.values(
        'producto__nombre', 
        'producto__categoria'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:top_n]
    
    context = {
        'form': form,
        'productos_vendidos': productos_vendidos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'top_n': top_n,
    }
    return render(request, 'reportes/reporteProductos.html', context)

@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista', 'estilista']))
def reporte_stock_bajo(request):
    """Reporte de productos bajo stock mínimo"""
    productos_bajo_minimo = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        estado='activo'
    ).order_by('stock_actual')
    
    context = {
        'productos': productos_bajo_minimo,
    }
    # La plantilla actual se llama `reportesStockBajo.html` en el proyecto
    return render(request, 'reportes/reportesStockBajo.html', context)


@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista', 'estilista']))
def exportar_inventario_csv(request):
    """Exporta el conjunto filtrado de inventario (basado en GET params) como CSV compatible con Excel."""
    productos = Producto.objects.all()
    tipo_reporte = request.GET.get('tipo_reporte')
    if tipo_reporte == 'bajo_minimo':
        productos = productos.filter(stock_actual__lte=F('stock_minimo'))
    # otros filtros se pueden aplicar igual que en `reporte_inventario`

    # Registrar acción
    registrar_accion(request.user, 'exportar_inventario_csv', modelo='Producto', descripcion=f'Export {productos.count()} items')

    # Crear CSV
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Nombre', 'Categoria', 'Precio Costo', 'Precio Venta', 'Stock Actual', 'Stock Minimo', 'Proveedor', 'Estado'])
    for p in productos:
        proveedor = p.proveedor.nombre_empresa if p.proveedor else ''
        writer.writerow([p.nombre, p.categoria, str(p.precio_costo), str(p.precio_venta), p.stock_actual, p.stock_minimo, proveedor, p.estado])

    response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.csv"'
    return response


@login_required
@user_passes_test(lambda u: has_any_role(u, ['administrador', 'recepcionista', 'estilista']))
def exportar_inventario_pdf(request):
    """Intenta generar un PDF con ReportLab; si no está disponible, devuelve un mensaje instructivo."""
    productos = Producto.objects.filter(stock_actual__lte=F('stock_minimo'), estado='activo')
    registrar_accion(request.user, 'exportar_inventario_pdf', modelo='Producto', descripcion=f'Export PDF {productos.count()} items')

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        return HttpResponse('La exportación a PDF requiere la librería "reportlab". Instale con: pip install reportlab', status=500)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, 'Reporte de Inventario - Stock Bajo')
    y -= 30
    c.setFont('Helvetica', 10)
    for p in productos:
        text = f"{p.nombre} | Stock: {p.stock_actual} | Min: {p.stock_minimo} | Proveedor: {p.proveedor.nombre_empresa if p.proveedor else '-'}"
        c.drawString(40, y, text[:110])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 40
    c.save()
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'
    return response

@login_required
def historial_reportes(request):
    """Muestra el historial de reportes generados"""
    reportes = Reporte.objects.filter(usuario=request.user)
    
    context = {
        'reportes': reportes,
    }
    return render(request, 'reportes/historialReportes.html', context)