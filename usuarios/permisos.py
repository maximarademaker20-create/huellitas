from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

RECEPCION = 'recepcion'
VETERINARIO = 'veterinario'


def rol_de(usuario):
    perfil = getattr(usuario, 'perfil', None)
    if perfil is None:
        return ''
    return perfil.rol


def tiene_rol(usuario, roles):
    return usuario.is_superuser or rol_de(usuario) in roles


def solo_rol(*roles, aviso='No tenés permiso para hacer esa acción.'):
    def decorador(vista):
        @wraps(vista)
        def envoltorio(request, *args, **kwargs):
            if not tiene_rol(request.user, roles):
                messages.error(request, aviso)
                return redirect('inicio')
            return vista(request, *args, **kwargs)
        return envoltorio
    return decorador
