from datetime import date

from django.db import models


class Especie(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_especie')
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'especie'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Raza(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_raza')
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='razas', db_column='id_especie')
    nombre = models.CharField(max_length=60)

    class Meta:
        db_table = 'raza'
        ordering = ['especie__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'especie'], name='uq_raza_especie'),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.especie})'


class Dueno(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_dueno')
    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
    dni = models.CharField('DNI', max_length=10, unique=True)
    telefono = models.CharField('teléfono', max_length=20, help_text='Se usa para los recordatorios por WhatsApp')
    direccion = models.CharField('dirección', max_length=150, blank=True)
    email = models.EmailField(max_length=100, blank=True)

    class Meta:
        db_table = 'dueno'
        verbose_name = 'dueño'
        verbose_name_plural = 'dueños'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Mascota(models.Model):
    SEXO = [('H', 'Hembra'), ('M', 'Macho')]
    ESTADO = [('activo', 'Activo'), ('baja', 'Baja')]

    id = models.AutoField(primary_key=True, db_column='id_mascota')
    raza = models.ForeignKey(Raza, on_delete=models.PROTECT, related_name='mascotas', db_column='id_raza')
    dueno = models.ForeignKey(Dueno, on_delete=models.PROTECT, related_name='mascotas', verbose_name='dueño', db_column='id_dueno')
    nombre = models.CharField(max_length=60)
    sexo = models.CharField(max_length=1, choices=SEXO)
    fecha_nacimiento = models.DateField('fecha de nacimiento', null=True, blank=True)
    color = models.CharField('color / señas particulares', max_length=80, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO, default='activo')
    fecha_alta = models.DateField('fecha de alta', default=date.today)
    fecha_baja = models.DateField('fecha de baja', null=True, blank=True)
    motivo_baja = models.CharField('motivo de baja', max_length=150, blank=True)

    class Meta:
        db_table = 'mascota'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def dar_de_baja(self, motivo):
        self.estado = 'baja'
        self.fecha_baja = date.today()
        self.motivo_baja = motivo
        self.save()

    def reactivar(self):
        self.estado = 'activo'
        self.fecha_baja = None
        self.motivo_baja = ''
        self.save()

    def historial(self):
        eventos = [{'tipo': 'consulta', 'fecha': c.fecha, 'obj': c} for c in self.consultas.all()]
        eventos += [{'tipo': 'vacuna', 'fecha': v.fecha_aplicacion, 'obj': v}
                    for v in self.vacunas.select_related('vacuna')]
        return sorted(eventos, key=lambda e: e['fecha'], reverse=True)

    @property
    def especie(self):
        return self.raza.especie

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        n = self.fecha_nacimiento
        return hoy.year - n.year - ((hoy.month, hoy.day) < (n.month, n.day))


class Consulta(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_consulta')
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, related_name='consultas', db_column='id_mascota')
    fecha = models.DateField(default=date.today)
    peso = models.DecimalField('peso (kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    motivo = models.CharField(max_length=150)
    diagnostico = models.TextField('diagnóstico')
    tratamiento = models.TextField(blank=True)

    class Meta:
        db_table = 'consulta'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.mascota} - {self.fecha:%d/%m/%Y} - {self.motivo}'


class Vacuna(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_vacuna')
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.CharField('descripción', max_length=200, blank=True)

    class Meta:
        db_table = 'vacuna'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class VacunaAplicada(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_vacuna_aplicada')
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, related_name='vacunas', db_column='id_mascota')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.PROTECT, db_column='id_vacuna')
    fecha_aplicacion = models.DateField('fecha de aplicación', default=date.today)
    proxima_dosis = models.DateField('próxima dosis', null=True, blank=True, help_text='Dejar vacío si es dosis única')

    class Meta:
        db_table = 'vacuna_aplicada'
        verbose_name = 'vacuna aplicada'
        verbose_name_plural = 'vacunas aplicadas'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f'{self.mascota} - {self.vacuna} ({self.fecha_aplicacion:%d/%m/%Y})'


class Turno(models.Model):
    ESTADO = [('pendiente', 'Pendiente'), ('atendido', 'Atendido'), ('cancelado', 'Cancelado')]

    id = models.AutoField(primary_key=True, db_column='id_turno')
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, related_name='turnos', db_column='id_mascota')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=150, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO, default='pendiente')

    class Meta:
        db_table = 'turno'
        ordering = ['fecha', 'hora']
        constraints = [
            models.UniqueConstraint(fields=['fecha', 'hora'], name='uq_turno_horario'),
        ]

    def __str__(self):
        return f'{self.fecha:%d/%m/%Y} {self.hora:%H:%M} - {self.mascota}'


class Recordatorio(models.Model):
    TIPO = [('turno', 'Turno'), ('vacuna', 'Vacuna'), ('agenda', 'Agenda del día')]
    ESTADO = [('pendiente', 'Pendiente'), ('enviado', 'Enviado'), ('fallido', 'Fallido')]

    id = models.AutoField(primary_key=True, db_column='id_recordatorio')
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, null=True, blank=True, related_name='recordatorios', db_column='id_turno')
    vacuna_aplicada = models.ForeignKey(VacunaAplicada, on_delete=models.CASCADE, null=True, blank=True, related_name='recordatorios', db_column='id_vacuna_aplicada')
    tipo = models.CharField(max_length=10, choices=TIPO)
    fecha_envio = models.DateTimeField('fecha de envío', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO, default='pendiente')

    class Meta:
        db_table = 'recordatorio'
        ordering = ['-fecha_envio']

    def __str__(self):
        destino = self.turno or self.vacuna_aplicada
        return f'Recordatorio de {self.get_tipo_display().lower()}: {destino}'
