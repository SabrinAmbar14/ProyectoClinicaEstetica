from django import forms
from django.core.exceptions import ValidationError
from .models import Colaborador
import re

class ColaboradorForm(forms.ModelForm):
    
    class Meta:
        model = Colaborador
        fields = [
            'rut', 'nombre', 'apellido', 'email', 'telefono',
            'cargo', 'fecha_contratacion', 'sueldo', 'direccion'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678-9'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'colaborador@clinica.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_contratacion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'sueldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'direccion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Ingrese la dirección completa'
            }),
        }
        labels = {
            'fecha_contratacion': 'Fecha de Contratación',
        }
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            rut_pattern = re.compile(r'^\d{7,8}-[\dkK]$')
            if not rut_pattern.match(rut):
                raise ValidationError('El RUT debe tener el formato: 12345678-9')
            
            if self.instance and self.instance.pk:
                if Colaborador.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
                    raise ValidationError('Este RUT ya está registrado')
            else:
                if Colaborador.objects.filter(rut=rut).exists():
                    raise ValidationError('Este RUT ya está registrado')
        
        return rut
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
            if not re.match(r'^[\+\d]{8,15}$', telefono_limpio):
                raise ValidationError('Formato de teléfono inválido')
        return telefono

class BuscarColaboradorForm(forms.Form):
    TIPO_BUSQUEDA_CHOICES = [
        ('nombre', 'Por Nombre'),
        ('rut', 'Por RUT'),
        ('cargo', 'Por Cargo'),
    ]
    
    tipo_busqueda = forms.ChoiceField(
        choices=TIPO_BUSQUEDA_CHOICES,
        initial='nombre',
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