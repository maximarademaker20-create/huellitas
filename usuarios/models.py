from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    ROLES = [('recepcion', 'Recepción'), ('veterinario', 'Veterinario/a')]

    id = models.AutoField(primary_key=True, db_column='id_perfil')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', db_column='id_usuario')
    rol = models.CharField(max_length=15, choices=ROLES, default='recepcion')
    telefono = models.CharField('teléfono', max_length=20, blank=True,
                                help_text='Se usa para enviarle la agenda del día por WhatsApp')

    class Meta:
        db_table = 'perfil'
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'
