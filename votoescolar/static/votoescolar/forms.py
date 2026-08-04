from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Candidatura, Estudiante, Voto


class CandidaturaForm(forms.ModelForm):
    class Meta:
        model = Candidatura
        fields = [
            'nombre_lista',
            'eslogan',
            'presidente',
            'foto_lista',
            'plan_trabajo',
            'color_representativo',
            'estado',
        ]

    def clean_plan_trabajo(self):
        plan = self.cleaned_data.get('plan_trabajo')
        if plan:
            if plan.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo PDF no puede superar los 10 MB.')
            if not plan.name.lower().endswith('.pdf'):
                raise forms.ValidationError('El plan de trabajo debe ser un archivo PDF.')
        return plan


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['usuario', 'cedula', 'grado', 'paralelo', 'foto_credencial', 'ha_votado']


class VotoForm(forms.ModelForm):
    class Meta:
        model = Voto
        fields = ['eleccion']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
