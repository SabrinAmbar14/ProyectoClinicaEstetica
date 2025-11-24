from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Servicio, Cita, ProductoConsumido
from clientes.models import Cliente
from inventario.models import Producto

class ServicioForm(forms.ModelForm):
    
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'categoria', 'precio_base', 'duracion_minutos']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del servicio'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción del servicio'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'precio_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'duracion_minutos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': '1'
            }),
        }
        labels = {
            'precio_base': 'Precio Base',
            'duracion_minutos': 'Duración (minutos)',
        }

class CitaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(estado='activo'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Cita
        fields = ['cliente', 'servicio', 'estilista', 'fecha_cita', 'observaciones']
        widgets = {
            'servicio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estilista': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_cita': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Observaciones adicionales'
            }),
        }
    
    def clean_fecha_cita(self):
        fecha_cita = self.cleaned_data.get('fecha_cita')
        if fecha_cita and fecha_cita < timezone.now():
            raise ValidationError('La fecha de la cita no puede ser en el pasado')
        return fecha_cita

class ProductoConsumidoForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado='activo', stock_actual__gt=0),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ProductoConsumido
        fields = ['producto', 'cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1',
                'min': '1'
            }),
        }
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')
        
        if producto and cantidad:
            if cantidad > producto.stock_actual:
                raise ValidationError(f'Stock insuficiente. Solo hay {producto.stock_actual} unidades disponibles.')
        
        return cantidad

class CalcularServicioForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(estado='activo'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(estado='activo'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_cita = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.filter(estado='activo', stock_actual__gt=0),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )


class RegistrarServiciosMultipleForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(estado='activo'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    servicios = forms.ModelMultipleChoiceField(
        queryset=Servicio.objects.filter(estado='activo'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    fecha_cita = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

class BuscarServicioForm(forms.Form):
    TIPO_BUSQUEDA_CHOICES = [
        ('nombre', 'Por Nombre'),
        ('categoria', 'Por Categoría'),
        ('precio', 'Por Precio'),
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
    precio_maximo = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio máximo',
            'step': '0.01'
        })
    )