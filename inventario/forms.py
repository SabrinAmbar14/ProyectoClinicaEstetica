from django import forms
from django.core.exceptions import ValidationError
from .models import Producto, MovimientoInventario

class ProductoForm(forms.ModelForm):
    
    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'categoria', 'precio_costo',
            'precio_venta', 'stock_actual', 'stock_minimo', 'proveedor'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción del producto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'precio_costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'precio_costo': 'Precio de Costo',
            'precio_venta': 'Precio de Venta',
            'stock_actual': 'Stock Actual',
            'stock_minimo': 'Stock Mínimo',
        }
    
    def clean_precio_venta(self):
        precio_venta = self.cleaned_data.get('precio_venta')
        precio_costo = self.cleaned_data.get('precio_costo')
        
        if precio_venta and precio_costo and precio_venta <= precio_costo:
            raise ValidationError('El precio de venta debe ser mayor al precio de costo')
        
        return precio_venta

class MovimientoInventarioForm(forms.ModelForm):
    
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo_movimiento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '1'
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Motivo del movimiento'
            }),
        }

class ActualizarStockForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cantidad a agregar'
        })
    )
    motivo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Motivo de la reposición'
        })
    )

class BuscarProductoForm(forms.Form):
    TIPO_BUSQUEDA_CHOICES = [
        ('nombre', 'Por Nombre'),
        ('categoria', 'Por Categoría'),
        ('bajo_minimo', 'Bajo Stock Mínimo'),
    ]
    
    tipo_busqueda = forms.ChoiceField(
        choices=TIPO_BUSQUEDA_CHOICES,
        initial='nombre',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    termino_busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese término de búsqueda...',
            'class': 'form-control'
        })
    )