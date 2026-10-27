from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import Perfil


def registrar(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
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
            datos = {'errores': errores, 'valores': request.POST, 'roles': Perfil.ROLES}
            return render(request, 'usuarios/registrar.html', datos)

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre,
            last_name=apellido,
        )
        Perfil.objects.create(usuario=usuario, rol=rol)
        print(f'>>> Usuario creado: {usuario.username} ({rol})')
        messages.success(request, f'Cuenta creada para {usuario.username}. Ya podés iniciar sesión.')
        return redirect('login')

    datos = {'roles': Perfil.ROLES}
    return render(request, 'usuarios/registrar.html', datos)
