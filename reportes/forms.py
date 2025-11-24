from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

class ReporteInventarioForm(forms.Form):
    TIPO_REPORTE_CHOICES = [
        ('general', 'Inventario General'),
        ('bajo_minimo', 'Productos Bajo Stock Mínimo'),
        ('categoria', 'Por Categoría'),
        ('proveedor', 'Por Proveedor'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='general',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categoria = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas las categorías'),
            ('champu', 'Champú'),
            ('acondicionador', 'Acondicionador'),
            ('tinte', 'Tinte'),
            ('laca', 'Laca'),
            ('crema', 'Crema'),
            ('tratamiento', 'Tratamiento'),
            ('otros', 'Otros'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    incluir_inactivos = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class ReporteVentasForm(forms.Form):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValidationError('La fecha de inicio no puede ser mayor a la fecha de fin')
            
            # Validar que el rango no sea mayor a 1 año
            if (fecha_fin - fecha_inicio).days > 365:
                raise ValidationError('El rango de fechas no puede ser mayor a 1 año')
        
        return cleaned_data

class ReporteClientesForm(forms.Form):
    TIPO_REPORTE_CHOICES = [
        ('activos', 'Clientes Activos'),
        ('inactivos', 'Clientes Inactivos'),
        ('cumpleanos', 'Cumpleaños del Mes'),
        ('todos', 'Todos los Clientes'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='activos',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ordenar_por = forms.ChoiceField(
        choices=[
            ('nombre', 'Nombre'),
            ('fecha_registro', 'Fecha de Registro'),
            ('estado', 'Estado'),
        ],
        initial='nombre',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ReporteProductosForm(forms.Form):
    PERIODO_CHOICES = [
        ('hoy', 'Hoy'),
        ('semana', 'Esta Semana'),
        ('mes', 'Este Mes'),
        ('trimestre', 'Este Trimestre'),
        ('anio', 'Este Año'),
        ('personalizado', 'Personalizado'),
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        initial='mes',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    top_n = forms.IntegerField(
        min_value=5,
        max_value=50,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '10'
        })
    )