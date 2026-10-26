from django.contrib import admin

from .models import (Consulta, Dueno, Especie, Mascota, Raza, Recordatorio,
                     Turno, Vacuna, VacunaAplicada)


class RazaInline(admin.TabularInline):
    model = Raza
    extra = 1


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    inlines = [RazaInline]


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie']
    list_filter = ['especie']
    search_fields = ['nombre']


@admin.register(Dueno)
class DuenoAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'dni', 'telefono']
    search_fields = ['nombre', 'apellido', 'dni']


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'raza', 'dueno', 'estado']
    list_filter = ['estado', 'raza__especie']
    search_fields = ['nombre', 'dueno__nombre', 'dueno__apellido', 'dueno__dni']


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'mascota', 'motivo']
    search_fields = ['mascota__nombre', 'motivo']


@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']


@admin.register(VacunaAplicada)
class VacunaAplicadaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'vacuna', 'fecha_aplicacion', 'proxima_dosis']
    list_filter = ['vacuna']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'hora', 'mascota', 'motivo', 'estado']
    list_filter = ['estado', 'fecha']


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'turno', 'vacuna_aplicada', 'fecha_envio', 'estado']
    list_filter = ['tipo', 'estado']
