from django.shortcuts import render, redirect
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import timedelta
from clientes.models import Cliente
from inventario.models import Producto, MovimientoInventario
from servicios.models import Servicio, Cita
from colaboradores.models import Colaborador
from proveedores.models import Proveedor
import json

def index(request):
    # Redirigir a login si el usuario no está autenticado
    if not request.user.is_authenticated:
        return redirect('/usuarios/')
    
    # KPIs principales
    total_clientes = Cliente.objects.filter(estado='activo').count()
    total_productos = Producto.objects.filter(estado='activo').count()
    total_colaboradores = Colaborador.objects.filter(estado='activo').count()
    total_proveedores = Proveedor.objects.filter(estado='activo').count()
    
    # Stock bajo mínimo
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        estado='activo'
    ).count()
    
    # Citas de hoy y pendientes
    hoy = timezone.now().date()
    citas_hoy = Cita.objects.filter(fecha_cita__date=hoy).count()
    citas_pendientes = Cita.objects.filter(estado='programada').count()
    
    # Valor total del inventario
    productos_activos = Producto.objects.filter(estado='activo')
    valor_inventario = sum(p.precio_costo * p.stock_actual for p in productos_activos)
    
    # Datos para gráfico de productos por categoría (ordenados alfabéticamente)
    productos_por_categoria = Producto.objects.filter(estado='activo').values('categoria').annotate(
        total=Count('id')
    ).order_by('categoria')
    
    # Obtener nombres legibles de las categorías
    categoria_dict = dict(Producto.CATEGORIA_CHOICES)
    categorias = [categoria_dict.get(p['categoria'], p['categoria']) for p in productos_por_categoria]
    cantidades_productos = [p['total'] for p in productos_por_categoria]
    
    # Datos para gráfico de clientes activos vs inactivos
    clientes_activos = Cliente.objects.filter(estado='activo').count()
    clientes_inactivos = Cliente.objects.filter(estado='inactivo').count()
    
    # Datos para gráfico de movimientos de inventario (últimos 7 días)
    fecha_hace_7_dias = timezone.now() - timedelta(days=7)
    movimientos_recientes = MovimientoInventario.objects.filter(
        fecha_movimiento__gte=fecha_hace_7_dias
    ).values('tipo_movimiento').annotate(
        total=Count('id')
    )
    
    movimientos_dict = {m['tipo_movimiento']: m['total'] for m in movimientos_recientes}
    
    # Productos con menor stock (top 5)
    productos_criticos = Producto.objects.filter(estado='activo').order_by('stock_actual')[:5]
    
    # Citas por estado
    citas_por_estado = Cita.objects.values('estado').annotate(
        total=Count('id')
    )
    
    context = {
        # KPIs
        'total_clientes': total_clientes,
        'total_productos': total_productos,
        'total_colaboradores': total_colaboradores,
        'total_proveedores': total_proveedores,
        'productos_bajo_stock': productos_bajo_stock,
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes,
        'valor_inventario': valor_inventario,
        
        # Datos para gráficos (convertir a JSON)
        'categorias_json': json.dumps(categorias),
        'cantidades_productos_json': json.dumps(cantidades_productos),
        'clientes_activos': clientes_activos,
        'clientes_inactivos': clientes_inactivos,
        
        # Movimientos
        'entradas': movimientos_dict.get('entrada', 0),
        'salidas': movimientos_dict.get('salida', 0),
        'ajustes': movimientos_dict.get('ajuste', 0),
        
        # Productos críticos
        'productos_criticos': productos_criticos,
        
        # Citas por estado
        'citas_por_estado': citas_por_estado,
    }
    
    return render(request, 'core/dashboard.html', context)