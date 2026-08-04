from django import forms
from django.contrib.auth.models import User
from .models import Candidatura, Estudiante, Voto, ProcesoElectoral


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
        labels = {
            'nombre_lista': 'Nombre de la Lista / Partido',
            'eslogan': 'Eslogan',
            'presidente': 'Presidente / Candidato Principal',
            'foto_lista': 'Foto / Logotipo de la Lista',
            'plan_trabajo': 'Plan de Trabajo (PDF)',
            'color_representativo': 'Color Representativo',
            'estado': 'Estado de Candidatura',
        }
        widgets = {
            'nombre_lista': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Lista 1 - Juventud Activa'}),
            'eslogan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Por una educación inclusiva y moderna'}),
            'presidente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del presidente'}),
            'foto_lista': forms.FileInput(attrs={'class': 'form-control'}),
            'plan_trabajo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'color_representativo': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_plan_trabajo(self):
        plan = self.cleaned_data.get('plan_trabajo')
        if plan:
            # Validar extensión obligatoria .pdf
            if not plan.name.lower().endswith('.pdf'):
                raise forms.ValidationError('El plan de trabajo debe ser obligatoriamente un archivo en formato PDF (.pdf).')
            # Validar tamaño máximo 10 MB
            if plan.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo PDF del Plan de Trabajo no puede superar los 10 MB de tamaño.')
        return plan


class EstudianteForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de Usuario (Login)",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. est_juangomez'})
    )
    first_name = forms.CharField(
        label="Nombres",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan Alberto'})
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gómez Pérez'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'estudiante@colegio.edu.ec'})
    )
    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        help_text="Requerida al crear. En edición, déjala en blanco si no deseas modificarla."
    )

    class Meta:
        model = Estudiante
        fields = ['cedula_matricula', 'grado_curso', 'paralelo', 'foto_credencial', 'ha_votado']
        labels = {
            'cedula_matricula': 'Cédula / Matrícula (Única)',
            'grado_curso': 'Grado / Curso',
            'paralelo': 'Paralelo',
            'foto_credencial': 'Foto de Credencial',
            'ha_votado': '¿Ha emitido su voto?',
        }
        widgets = {
            'cedula_matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1712345678'}),
            'grado_curso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3er Año BGU'}),
            'paralelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. A'}),
            'foto_credencial': forms.FileInput(attrs={'class': 'form-control'}),
            'ha_votado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Si es un estudiante nuevo y el usuario ya existe en Django, lanzar error bonito
        if not self.instance.pk:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Este Nombre de Usuario ya está en uso. Por favor elige otro.')
        else:
            # Si se edita, verificar que no coincida con el de otro usuario existente
            if User.objects.filter(username=username).exclude(pk=self.instance.usuario.pk).exists():
                raise forms.ValidationError('Este Nombre de Usuario ya está en uso por otro estudiante.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Si estamos creando un nuevo estudiante, la contraseña es obligatoria
        if not self.instance.pk and not password:
            raise forms.ValidationError('Debes ingresar una contraseña para el nuevo estudiante.')
        return password


class VotoForm(forms.ModelForm):
    class Meta:
        model = Voto
        fields = ['eleccion']


class ProcesoElectoralForm(forms.ModelForm):
    class Meta:
        model = ProcesoElectoral
        fields = ['titulo', 'descripcion', 'estado', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }