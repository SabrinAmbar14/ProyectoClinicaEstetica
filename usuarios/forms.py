from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import PerfilUsuario
import re

class RegistroUsuarioForm(UserCreationForm):
    # Para el registro administrador mínimo: RUT, Nombre y contraseña
    rut = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9'
        }),
        label='RUT'
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        }),
        label='Nombre'
    )
    role = forms.ChoiceField(
        choices=PerfilUsuario.ROL_CHOICES,
        required=True,
        initial='recepcionista',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rol'
    )

    class Meta:
        model = User
        # Solo pedimos nombre y contraseña; el username será el RUT
        fields = ['first_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases bootstrap a los campos de contraseña para que se muestren bien
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    
    def clean_email(self):
        # Mantener para compatibilidad si el campo existe en otros formularios
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Este email ya está registrado')
        return email

    def clean_first_name(self):
        nombre = self.cleaned_data.get('first_name', '').strip()
        # Permitir sólo letras y espacios (acentos incluidos)
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", nombre):
            raise ValidationError('El nombre solo puede contener letras y espacios')
        return nombre

    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '').strip()
        if not rut:
            raise ValidationError('El RUT es obligatorio')
        # Validar unicidad: si ya existe un usuario con username==rut
        if User.objects.filter(username__iexact=rut).exists():
            raise ValidationError('Ya existe un usuario con ese RUT')
        return rut

    def _generar_username_unico(self, first_name, last_name):
        # Deprecated: ya no usamos esta función; conservada por compatibilidad
        base = (first_name + last_name).lower()
        username = re.sub(r"[^a-zA-ZÁÉÍÓÚáéíóúÑñÜü]", "", base)
        username = username.replace(' ', '')
        if not username:
            username = 'usuario'
        candidate = username
        suffix = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{username}{suffix}"
            suffix += 1
        return candidate

    def save(self, commit=True):
        # Crear usuario usando el RUT como username
        user = super().save(commit=False)
        rut = self.cleaned_data.get('rut')
        first_name = self.cleaned_data.get('first_name', '')
        user.username = rut
        user.first_name = first_name
        if commit:
            user.save()
        return user

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'telefono', 'direccion', 'fecha_nacimiento', 'fecha_contratacion']
        widgets = {
            'rol': forms.Select(attrs={
                'class': 'form-control'
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
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_contratacion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'fecha_contratacion': 'Fecha de Contratación',
        }

class EditarUsuarioForm(UserChangeForm):
    password = None  # Remover el campo de password del formulario
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    nuevo_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        nuevo_password = cleaned_data.get('nuevo_password')
        confirmar_password = cleaned_data.get('confirmar_password')
        
        if nuevo_password and confirmar_password and nuevo_password != confirmar_password:
            raise ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data

class BuscarUsuarioForm(forms.Form):
    TIPO_BUSQUEDA_CHOICES = [
        ('username', 'Por Usuario'),
        ('nombre', 'Por Nombre'),
        ('email', 'Por Email'),
        ('rol', 'Por Rol'),
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