from django import forms
from django.core.exceptions import ValidationError
from .models import Proveedor
import re

class ProveedorForm(forms.ModelForm):
    
    class Meta:
        model = Proveedor
        fields = [
            'rut', 'nombre_empresa', 'nombre_contacto', 'email',
            'telefono', 'direccion', 'productos_que_suministra'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678-9'
            }),
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto principal'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'proveedor@empresa.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'direccion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'productos_que_suministra': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Lista de productos que suministra este proveedor'
            }),
        }
        labels = {
            'nombre_empresa': 'Nombre de la Empresa',
            'nombre_contacto': 'Nombre del Contacto',
            'productos_que_suministra': 'Productos que Suministra',
        }
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            rut_pattern = re.compile(r'^\d{7,8}-[\dkK]$')
            if not rut_pattern.match(rut):
                raise ValidationError('El RUT debe tener el formato: 12345678-9')
            
            if self.instance and self.instance.pk:
                if Proveedor.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
                    raise ValidationError('Este RUT ya está registrado')
            else:
                if Proveedor.objects.filter(rut=rut).exists():
                    raise ValidationError('Este RUT ya está registrado')
        
        return rut
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
            if not re.match(r'^[\+\d]{8,15}$', telefono_limpio):
                raise ValidationError('Formato de teléfono inválido')
        return telefono

class BuscarProveedorForm(forms.Form):
    TIPO_BUSQUEDA_CHOICES = [
        ('empresa', 'Por Empresa'),
        ('contacto', 'Por Contacto'),
        ('rut', 'Por RUT'),
    ]
    
    tipo_busqueda = forms.ChoiceField(
        choices=TIPO_BUSQUEDA_CHOICES,
        initial='empresa',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    termino_busqueda = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese término de búsqueda...',
            'class': 'form-control'
        })
    )
    
    def clean_termino_busqueda(self):
        termino = self.cleaned_data.get('termino_busqueda')
        if len(termino.strip()) < 2:
            raise ValidationError('El término de búsqueda debe tener al menos 2 caracteres')
        return termino.strip()