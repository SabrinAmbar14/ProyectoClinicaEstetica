from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.helpers import is_admin_user, has_any_role
from django.db.models import Q
from .models import Colaborador
from .forms import ColaboradorForm, BuscarColaboradorForm
from usuarios.helpers import registrar_accion
from django.contrib.auth.decorators import user_passes_test

@login_required
def lista_colaboradores(request):
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'administrador')
    if is_admin:
        colaboradores = Colaborador.objects.all()
    else:
        # Usuarios no administradores sólo ven su propio registro si existe
        colaborador = getattr(user, 'colaborador', None)
        if colaborador:
            colaboradores = Colaborador.objects.filter(pk=colaborador.pk)
        else:
            colaboradores = Colaborador.objects.none()

    context = {
        'colaboradores': colaboradores,
    }
    return render(request, 'colaboradores/listaColaboradores.html', context)

@login_required
@user_passes_test(is_admin_user)
def agregar_colaborador(request):
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save()
            messages.success(request, 'Colaborador agregado exitosamente.')
            return redirect('colaboradores:lista_colaboradores')
    else:
        form = ColaboradorForm()
    
    context = {
        'form': form,
    }
    return render(request, 'colaboradores/formularioColaborador.html', context)

@login_required
@user_passes_test(is_admin_user)
def modificar_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador actualizado exitosamente.')
            return redirect('colaboradores:lista_colaboradores')
    else:
        form = ColaboradorForm(instance=colaborador)
    
    context = {
        'form': form,
        'colaborador': colaborador,
    }
    return render(request, 'colaboradores/formularioColaborador.html', context)

@login_required
@user_passes_test(is_admin_user)
def dar_baja_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    
    if request.method == 'POST':
        colaborador.estado = 'inactivo'
        colaborador.save()
        messages.success(request, 'Colaborador dado de baja exitosamente.')
        return redirect('colaboradores:lista_colaboradores')
    
    context = {
        'colaborador': colaborador,
    }
    return render(request, 'colaboradores/listaColaboradores.html', context)


@login_required
@user_passes_test(is_admin_user)
def eliminar_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    if request.method == 'POST':
        if colaborador.estado != 'activo':
            colaborador.delete()
            messages.success(request, 'Colaborador eliminado correctamente.')
            registrar_accion(request.user, 'eliminar_colaborador', modelo='Colaborador', objeto_id=pk,
                             descripcion=f"Colaborador {colaborador.rut} eliminado")
        else:
            messages.error(request, 'No se puede eliminar un colaborador activo. Primero desactívelo.')
        return redirect('colaboradores:lista_colaboradores')
    return render(request, 'colaboradores/listaColaboradores.html', {'colaborador': colaborador})

@login_required
def buscar_colaborador(request):
    colaboradores = None
    form = BuscarColaboradorForm(request.GET or None)
    
    if request.GET and form.is_valid():
        tipo_busqueda = form.cleaned_data['tipo_busqueda']
        termino = form.cleaned_data['termino_busqueda']
        
        if tipo_busqueda == 'nombre':
            colaboradores = Colaborador.objects.filter(
                Q(nombre__icontains=termino) | Q(apellido__icontains=termino)
            )
        elif tipo_busqueda == 'rut':
            colaboradores = Colaborador.objects.filter(rut__icontains=termino)
        elif tipo_busqueda == 'cargo':
            colaboradores = Colaborador.objects.filter(cargo__icontains=termino)
    
    context = {
        'form': form,
        'colaboradores': colaboradores,
    }
    return render(request, 'colaboradores/buscarColaborador.html', context)