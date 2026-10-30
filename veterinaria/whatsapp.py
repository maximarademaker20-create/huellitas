from urllib.parse import quote


def numero_internacional(telefono):
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


def mensaje_agenda(dia, turnos):
    MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
             'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    texto = f'AGENDA DEL {dia.day} DE {MESES[dia.month - 1].upper()}\n'
    texto += 'Veterinaria Huellitas\n\n'

    if not turnos:
        return texto + 'No hay turnos agendados para este día.'

    for t in turnos:
        texto += f'{t.hora:%H:%M} - {t.mascota.nombre}'
        texto += f' ({t.mascota.raza.nombre})'
        texto += f'\n   Dueño: {t.mascota.dueno} - Tel: {t.mascota.dueno.telefono}'
        if t.motivo:
            texto += f'\n   Motivo: {t.motivo}'
        texto += '\n\n'

    total = len(turnos)
    texto += f'Total: {total} turno{"s" if total != 1 else ""}. 🐾'
    return texto
