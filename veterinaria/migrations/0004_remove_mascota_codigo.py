from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('veterinaria', '0003_mascota_codigo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mascota',
            name='codigo',
        ),
    ]
