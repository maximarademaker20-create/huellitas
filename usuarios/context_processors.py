from .permisos import RECEPCION, VETERINARIO, rol_de, tiene_rol


def roles(request):
    usuario = getattr(request, 'user', None)
    if usuario is None or not usuario.is_authenticated:
        return {}
    return {
        'rol_actual': rol_de(usuario),
        'puede_recepcion': tiene_rol(usuario, [RECEPCION]),
        'puede_historia': tiene_rol(usuario, [VETERINARIO]),
    }
