from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from veterinaria.models import (Consulta, Dueno, Especie, Mascota, Raza, Turno,
                                Vacuna, VacunaAplicada)


class Command(BaseCommand):
    help = 'Carga especies, razas, dueños, mascotas, consultas, vacunas y turnos de ejemplo'

    def handle(self, *args, **opciones):
        if Mascota.objects.exists():
            self.stdout.write(self.style.WARNING('Ya hay mascotas cargadas: no se agregó nada.'))
            return

        hoy = date.today()

        razas = {}
        for especie, lista in {'Perro': ['Caniche', 'Labrador', 'Beagle', 'Mestizo', 'Golden retriever'],
                               'Gato': ['Siamés', 'Persa', 'Común europeo'],
                               'Ave': ['Canario', 'Cotorra']}.items():
            e = Especie.objects.create(nombre=especie)
            for r in lista:
                razas[r] = Raza.objects.create(nombre=r, especie=e)

        vac = {n: Vacuna.objects.create(nombre=n, descripcion=d) for n, d in [
            ('Antirrábica', 'Anual, obligatoria'),
            ('Séxtuple', 'Perros: moquillo, parvovirus, hepatitis y otras'),
            ('Triple felina', 'Gatos: panleucopenia, rinotraqueítis y calicivirus'),
            ('Tos de las perreras', 'Perros, anual'),
        ]}

        d = {}
        for nombre, apellido, dni, tel in [('Laura', 'Gómez', '30456789', '3415551234'),
                                           ('Juan', 'Pérez', '28123456', '3415552345'),
                                           ('Ana', 'Díaz', '35987654', '3415553456'),
                                           ('Carlos', 'Ruiz', '32654321', '3415554567'),
                                           ('Sofía', 'Martín', '40111222', '3415555678'),
                                           ('Pedro', 'Sosa', '37333444', '3415556789')]:
            d[nombre] = Dueno.objects.create(nombre=nombre, apellido=apellido, dni=dni, telefono=tel)

        m = {}
        for nombre, sexo, nac, raza, dueno, color in [
                ('Luna', 'H', date(2021, 3, 12), 'Caniche', 'Laura', 'Blanca'),
                ('Michi', 'M', date(2020, 7, 5), 'Siamés', 'Juan', 'Crema'),
                ('Rocky', 'M', date(2019, 1, 20), 'Labrador', 'Ana', 'Dorado'),
                ('Kira', 'H', date(2022, 11, 14), 'Mestizo', 'Carlos', 'Negra y marrón'),
                ('Simba', 'M', date(2018, 8, 30), 'Persa', 'Sofía', 'Gris'),
                ('Nala', 'H', date(2023, 4, 9), 'Común europeo', 'Pedro', 'Atigrada')]:
            m[nombre] = Mascota.objects.create(nombre=nombre, sexo=sexo, fecha_nacimiento=nac, raza=razas[raza],
                                               dueno=d[dueno], color=color, fecha_alta=nac + timedelta(days=60))
        Mascota.objects.create(nombre='Toby', sexo='M', fecha_nacimiento=date(2017, 2, 2), raza=razas['Beagle'],
                               dueno=d['Laura'], color='Tricolor', estado='baja', fecha_alta=date(2017, 4, 11),
                               fecha_baja=hoy - timedelta(days=130), motivo_baja='Mudanza')

        for mascota, dias, peso, motivo, diag, trat in [
                ('Luna', 250, 6.1, 'Vómitos', 'Gastroenteritis leve', 'Dieta blanda 3 días'),
                ('Luna', 120, 6.2, 'Control anual', 'Sin novedades', ''),
                ('Luna', 3, 6.3, 'Se rasca la oreja', 'Otitis leve', 'Gotas óticas cada 12 h durante 7 días'),
                ('Rocky', 50, 31.5, 'Cojera', 'Esguince leve', 'Reposo y antiinflamatorio 5 días'),
                ('Michi', 15, 4.8, 'Control', 'Sin novedades', '')]:
            Consulta.objects.create(mascota=m[mascota], fecha=hoy - timedelta(days=dias), peso=peso,
                                    motivo=motivo, diagnostico=diag, tratamiento=trat)

        for mascota, vacuna, hace, proxima in [('Luna', 'Séxtuple', 205, 160), ('Luna', 'Antirrábica', 47, 318),
                                               ('Rocky', 'Antirrábica', 364, 1), ('Kira', 'Séxtuple', 362, 3),
                                               ('Simba', 'Triple felina', 360, 5)]:
            VacunaAplicada.objects.create(mascota=m[mascota], vacuna=vac[vacuna],
                                          fecha_aplicacion=hoy - timedelta(days=hace),
                                          proxima_dosis=hoy + timedelta(days=proxima))

        for mascota, dias, hora, motivo in [('Luna', 0, time(9, 0), 'Control'), ('Rocky', 0, time(10, 30), 'Vacuna antirrábica'),
                                            ('Michi', 0, time(11, 15), 'Consulta'), ('Kira', 0, time(15, 0), 'Control'),
                                            ('Nala', 1, time(16, 30), 'Consulta'), ('Simba', 5, time(9, 30), 'Vacuna'),
                                            ('Luna', 7, time(10, 0), 'Control otitis')]:
            Turno.objects.create(mascota=m[mascota], fecha=hoy + timedelta(days=dias), hora=hora, motivo=motivo)

        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados. ¡Listo para usar Huellitas!'))
