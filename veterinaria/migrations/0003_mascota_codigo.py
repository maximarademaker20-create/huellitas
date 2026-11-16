import uuid

from django.db import migrations, models


def asignar_codigos(apps, schema_editor):
    Mascota = apps.get_model('veterinaria', 'Mascota')
    for mascota in Mascota.objects.all():
        mascota.codigo = uuid.uuid4()
        mascota.save(update_fields=['codigo'])


class Migration(migrations.Migration):

    dependencies = [
        ('veterinaria', '0002_alter_recordatorio_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='mascota',
            name='codigo',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True,
                                   verbose_name='código del historial'),
        ),
        migrations.RunPython(asignar_codigos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='mascota',
            name='codigo',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True,
                                   verbose_name='código del historial'),
        ),
        migrations.AlterField(
            model_name='recordatorio',
            name='tipo',
            field=models.CharField(choices=[('turno', 'Turno'), ('vacuna', 'Vacuna'),
                                            ('agenda', 'Agenda del día'),
                                            ('historial', 'Historial clínico')],
                                   max_length=10),
        ),
    ]
