from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PerfilForm
from .models import Perfil


def registrar(request):
    desde_el_sistema = request.user.is_authenticated

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        errores = []
        if username == '' or password == '':
            errores.append('El usuario y la contraseña son obligatorios.')
        if User.objects.filter(username=username).exists():
            errores.append('Ese nombre de usuario ya existe. Elegí otro.')
        if len(password) < 8:
            errores.append('La contraseña tiene que tener al menos 8 caracteres.')
        if password != password2:
            errores.append('Las contraseñas no coinciden.')
        if rol not in dict(Perfil.ROLES):
            errores.append('Elegí si sos recepcionista o veterinario/a.')

        if errores:
            datos = {'errores': errores, 'valores': request.POST, 'roles': Perfil.ROLES,
                     'desde_el_sistema': desde_el_sistema}
            return render(request, 'usuarios/registrar.html', datos)

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre,
            last_name=apellido,
        )
        Perfil.objects.create(usuario=usuario, rol=rol, telefono=telefono)
        print(f'>>> Usuario creado: {usuario.username} ({rol})')
        if desde_el_sistema:
            messages.success(request, f'Se creó la cuenta de {usuario.get_full_name() or usuario.username}.')
            return redirect('personal')

        messages.success(request, f'Cuenta creada para {usuario.username}. Ya podés iniciar sesión.')
        return redirect('login')

    datos = {'roles': Perfil.ROLES, 'desde_el_sistema': desde_el_sistema}
    return render(request, 'usuarios/registrar.html', datos)


@login_required
def personal(request):
    buscar = request.GET.get("buscar", "")

    lista_usuarios = User.objects.select_related("perfil").order_by("first_name", "username")
    if buscar != "":
        lista_usuarios = lista_usuarios.filter(
            Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(username__icontains=buscar)
        )

    datos = {"usuarios": lista_usuarios, "buscar": buscar}
    return render(request, "usuarios/personal.html", datos)


@login_required
def perfil_form(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil, creado = Perfil.objects.get_or_create(usuario=usuario)
    form = PerfilForm(request.POST or None, instance=perfil)

    if request.method == "POST":
        print(">>> Llegó un POST para guardar un perfil")
        if form.is_valid():
            perfil = form.save()
            print(f">>> Perfil guardado: {perfil.usuario.username} - {perfil.rol} - {perfil.telefono}")
            messages.success(request, f"Se guardaron los datos de {usuario.get_full_name() or usuario.username}.")
            return redirect("personal")
        print(">>> No se guardó, hay errores:", form.errors.as_text())

    datos = {"form": form, "usuario": usuario}
    return render(request, "usuarios/perfil_form.html", datos)
