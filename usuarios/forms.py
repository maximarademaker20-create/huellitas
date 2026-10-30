from django import forms

from .models import Perfil


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['rol', 'telefono']
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: 3415551234'}),
        }
