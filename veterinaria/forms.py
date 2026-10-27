from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from .models import Consulta, Dueno, Especie, Mascota, Raza, Turno, VacunaAplicada


class FechaInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        super().__init__(format='%Y-%m-%d', **kwargs)


class DuenoForm(forms.ModelForm):
    class Meta:
        model = Dueno
        fields = ['nombre', 'apellido', 'dni', 'telefono', 'direccion', 'email']
        widgets = {
            'dni': forms.TextInput(attrs={'placeholder': 'Sin puntos'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: 3415551234'}),
        }
        error_messages = {'dni': {'unique': 'Ya hay un dueño registrado con ese DNI.'}}


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'fecha_nacimiento', 'raza', 'sexo', 'color', 'dueno']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Luna'}),
            'fecha_nacimiento': FechaInput(),
            'color': forms.TextInput(attrs={'placeholder': 'Ej: Blanca con mancha marrón'}),
        }


class BajaForm(forms.Form):
    MOTIVOS = [('Fallecimiento', 'Fallecimiento'), ('Mudanza', 'Mudanza'),
               ('Fin de la atención', 'Fin de la atención'), ('Otro', 'Otro')]
    motivo = forms.ChoiceField(label='Motivo de la baja', choices=MOTIVOS)


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['fecha', 'peso', 'motivo', 'diagnostico', 'tratamiento']
        widgets = {
            'fecha': FechaInput(),
            'peso': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Ej: 6.5'}),
            'motivo': forms.TextInput(attrs={'placeholder': 'Ej: Control, vómitos, cojera...'}),
            'diagnostico': forms.Textarea(attrs={'placeholder': 'Describí el diagnóstico...'}),
            'tratamiento': forms.Textarea(attrs={'placeholder': 'Medicación, dosis, duración, indicaciones...'}),
        }


class VacunaAplicadaForm(forms.ModelForm):
    class Meta:
        model = VacunaAplicada
        fields = ['vacuna', 'fecha_aplicacion', 'proxima_dosis']
        widgets = {
            'fecha_aplicacion': FechaInput(),
            'proxima_dosis': FechaInput(),
        }

    def clean(self):
        datos = super().clean()
        aplicacion, proxima = datos.get('fecha_aplicacion'), datos.get('proxima_dosis')
        if aplicacion and proxima and proxima <= aplicacion:
            self.add_error('proxima_dosis', 'La próxima dosis tiene que ser posterior a la aplicación.')
        return datos


class TurnoForm(forms.ModelForm):
    enviar_recordatorio = forms.BooleanField(
        label='Enviar recordatorio por WhatsApp al dueño', required=False, initial=True)

    class Meta:
        model = Turno
        fields = ['mascota', 'fecha', 'hora', 'motivo']
        widgets = {
            'fecha': FechaInput(),
            'hora': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'motivo': forms.TextInput(attrs={'placeholder': 'Ej: Control'}),
        }
        error_messages = {NON_FIELD_ERRORS: {'unique_together': 'Ya hay un turno a esa fecha y hora.'}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mascota'].queryset = Mascota.objects.filter(estado='activo').select_related('dueno')
        self.fields['mascota'].label_from_instance = lambda m: f'{m.nombre} — {m.dueno}'


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ['nombre']
        labels = {'nombre': 'Nueva especie'}
        widgets = {'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Conejo'})}


class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ['especie', 'nombre']
        labels = {'nombre': 'Nueva raza'}
        error_messages = {NON_FIELD_ERRORS: {'unique_together': 'Esa raza ya existe para esa especie.'}}
        widgets = {'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Bulldog francés'})}
