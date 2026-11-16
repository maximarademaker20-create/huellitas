import io

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

VIOLETA = colors.HexColor('#5E17EB')
VIOLETA_OSC = colors.HexColor('#4A0FC0')
VIOLETA_SUAVE = colors.HexColor('#F0E8FE')
AQUA_TEXTO = colors.HexColor('#0B8F87')
AQUA_SUAVE = colors.HexColor('#E3FEFC')
TEXTO = colors.HexColor('#1F1535')
TEXTO_SUAVE = colors.HexColor('#6B6485')
LINEA = colors.HexColor('#E8E2F5')


def estilos():
    base = getSampleStyleSheet()
    return {
        'titulo': ParagraphStyle('titulo', parent=base['Normal'], fontName='Helvetica-Bold',
                                 fontSize=20, textColor=VIOLETA, leading=24),
        'bajada': ParagraphStyle('bajada', parent=base['Normal'], fontName='Helvetica',
                                 fontSize=9, textColor=TEXTO_SUAVE, leading=13),
        'seccion': ParagraphStyle('seccion', parent=base['Normal'], fontName='Helvetica-Bold',
                                  fontSize=12, textColor=VIOLETA_OSC, leading=16, spaceAfter=6),
        'rotulo': ParagraphStyle('rotulo', parent=base['Normal'], fontName='Helvetica',
                                 fontSize=7.5, textColor=TEXTO_SUAVE, leading=10),
        'dato': ParagraphStyle('dato', parent=base['Normal'], fontName='Helvetica-Bold',
                               fontSize=10, textColor=TEXTO, leading=13),
        'fecha': ParagraphStyle('fecha', parent=base['Normal'], fontName='Helvetica-Bold',
                                fontSize=9, textColor=VIOLETA, leading=12),
        'cuerpo': ParagraphStyle('cuerpo', parent=base['Normal'], fontName='Helvetica',
                                 fontSize=9.5, textColor=TEXTO, leading=14),
        'pie': ParagraphStyle('pie', parent=base['Normal'], fontName='Helvetica',
                              fontSize=8, textColor=TEXTO_SUAVE, leading=11),
        'pie_der': ParagraphStyle('pie_der', parent=base['Normal'], fontName='Helvetica',
                                  fontSize=8, textColor=TEXTO_SUAVE, leading=11, alignment=TA_RIGHT),
        'encabezado': ParagraphStyle('encabezado', parent=base['Normal'], fontName='Helvetica-Bold',
                                     fontSize=8.5, textColor=colors.white, leading=11),
        'encabezado_der': ParagraphStyle('encabezado_der', parent=base['Normal'], fontName='Helvetica-Bold',
                                         fontSize=8.5, textColor=colors.white, leading=11, alignment=TA_RIGHT),
    }


def cabecera(est, hoy):
    logo = settings.BASE_DIR / 'static' / 'img' / 'logo_horizontal.png'
    izquierda = Image(str(logo), width=42 * mm, height=14 * mm) if logo.exists() else Paragraph('Huellitas', est['titulo'])
    derecha = [Paragraph('Historial clínico', est['titulo']),
               Paragraph(f'Emitido el {hoy:%d/%m/%Y}', est['bajada'])]
    tabla = Table([[izquierda, derecha]], colWidths=[52 * mm, 113 * mm])
    tabla.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEBELOW', (0, 0), (-1, -1), 1.4, colors.HexColor('#47FCF2')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tabla


def ficha_paciente(est, mascota):
    def celda(rotulo, valor):
        return [Paragraph(rotulo, est['rotulo']), Paragraph(str(valor), est['dato'])]

    columnas = [celda('Paciente', mascota.nombre), celda('Especie', mascota.especie),
                celda('Raza', mascota.raza.nombre), celda('Sexo', mascota.get_sexo_display())]
    if mascota.edad is not None:
        columnas.append(celda('Edad', f'{mascota.edad} años'))

    filas = [[c[0] for c in columnas], [c[1] for c in columnas]]
    ancho = 165 / len(columnas) * mm
    datos = Table(filas, colWidths=[ancho] * len(columnas))
    datos.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
    ]))

    dueno = Table([[Paragraph('Dueño', est['rotulo']),
                    Paragraph('Teléfono', est['rotulo'])],
                   [Paragraph(str(mascota.dueno), est['dato']),
                    Paragraph(mascota.dueno.telefono or '—', est['dato'])]],
                  colWidths=[82.5 * mm, 82.5 * mm])
    dueno.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
    ]))

    caja = Table([[datos], [dueno]], colWidths=[165 * mm])
    caja.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), VIOLETA_SUAVE),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#DECDFD')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
    ]))
    return caja


def tabla_historial(est, historial):
    encabezado = [Paragraph('Fecha', est['encabezado']),
                  Paragraph('Tipo', est['encabezado']),
                  Paragraph('Detalle', est['encabezado']),
                  Paragraph('Peso', est['encabezado_der'])]
    filas = [encabezado]
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), VIOLETA),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 1), (-1, -1), 0.4, LINEA),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]

    for e in historial:
        obj = e['obj']
        if e['tipo'] == 'consulta':
            detalle = f'<b>{obj.motivo}</b><br/><b>Diagnóstico:</b> {obj.diagnostico}'
            if obj.tratamiento:
                detalle += f'<br/><b>Tratamiento:</b> {obj.tratamiento}'
            tipo, peso = 'Consulta', (f'{obj.peso} kg' if obj.peso else '—')
        else:
            detalle = f'<b>Vacuna {obj.vacuna.nombre.lower()}</b>'
            detalle += (f'<br/>Próxima dosis: {obj.proxima_dosis:%d/%m/%Y}'
                        if obj.proxima_dosis else '<br/>Dosis única')
            tipo, peso = 'Vacuna', '—'

        filas.append([Paragraph(f'{e["fecha"]:%d/%m/%Y}', est['fecha']),
                      Paragraph(tipo, est['cuerpo']),
                      Paragraph(detalle, est['cuerpo']),
                      Paragraph(peso, est['cuerpo'])])
        fila = len(filas) - 1
        if e['tipo'] == 'vacuna':
            estilo.append(('BACKGROUND', (1, fila), (1, fila), AQUA_SUAVE))
            estilo.append(('TEXTCOLOR', (1, fila), (1, fila), AQUA_TEXTO))
        else:
            estilo.append(('BACKGROUND', (1, fila), (1, fila), VIOLETA_SUAVE))
            estilo.append(('TEXTCOLOR', (1, fila), (1, fila), VIOLETA))

    tabla = Table(filas, colWidths=[24 * mm, 22 * mm, 100 * mm, 19 * mm], repeatRows=1)
    tabla.setStyle(TableStyle(estilo))
    return tabla


def historial_pdf(mascota, historial, hoy):
    archivo = io.BytesIO()
    doc = SimpleDocTemplate(archivo, pagesize=A4,
                            leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title=f'Historial clínico de {mascota.nombre}',
                            author='Veterinaria Huellitas')
    est = estilos()
    partes = [cabecera(est, hoy), Spacer(1, 12), ficha_paciente(est, mascota), Spacer(1, 16)]

    if mascota.estado == 'baja':
        partes.append(Paragraph(
            f'Paciente dado de baja el {mascota.fecha_baja:%d/%m/%Y}. Su historial se conserva.',
            est['bajada']))
        partes.append(Spacer(1, 10))

    partes.append(Paragraph('Consultas y vacunas', est['seccion']))
    if historial:
        partes.append(tabla_historial(est, historial))
    else:
        partes.append(Paragraph('Todavía no hay consultas ni vacunas registradas.', est['cuerpo']))

    partes.append(Spacer(1, 18))
    pie = Table([[Paragraph('Documento informativo emitido por la veterinaria. '
                            'Ante cualquier duda, consultá con el profesional.', est['pie']),
                  Paragraph('Veterinaria Huellitas', est['pie_der'])]],
                colWidths=[115 * mm, 50 * mm])
    pie.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 0.6, LINEA),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    partes.append(pie)

    doc.build(partes)
    archivo.seek(0)
    return archivo
