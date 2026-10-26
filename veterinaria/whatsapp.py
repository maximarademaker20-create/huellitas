"""Arma los enlaces de WhatsApp (wa.me) con el mensaje ya escrito.

No hace falta ninguna cuenta ni servicio pago: el enlace abre WhatsApp
(web o en el celular) con el chat del dueño y el mensaje listo para enviar.
"""
from urllib.parse import quote


def numero_internacional(telefono):
    """Convierte un teléfono argentino al formato que pide WhatsApp.

    Ej: '341 555-1234' -> '5493415551234'
    """
    digitos = ''.join(c for c in telefono if c.isdigit())
    if digitos.startswith('0'):
        digitos = digitos[1:]
    if not digitos.startswith('54'):
        digitos = '549' + digitos
    return digitos


def enlace(telefono, mensaje):
    return f'https://wa.me/{numero_internacional(telefono)}?text={quote(mensaje)}'


def mensaje_turno(turno):
    dueno = turno.mascota.dueno
    texto = (f'¡Hola {dueno.nombre}! Te recordamos desde la veterinaria que {turno.mascota.nombre} '
             f'tiene turno el {turno.fecha:%d/%m/%Y} a las {turno.hora:%H:%M} hs')
    if turno.motivo:
        texto += f' ({turno.motivo.lower()})'
    return texto + '. ¡Te esperamos! 🐾'


def mensaje_vacuna(vacuna_aplicada):
    mascota = vacuna_aplicada.mascota
    return (f'¡Hola {mascota.dueno.nombre}! Te recordamos desde la veterinaria que a {mascota.nombre} '
            f'le corresponde la vacuna {vacuna_aplicada.vacuna.nombre.lower()} el '
            f'{vacuna_aplicada.proxima_dosis:%d/%m/%Y}. Podés pedir turno respondiendo este mensaje. 🐾')
