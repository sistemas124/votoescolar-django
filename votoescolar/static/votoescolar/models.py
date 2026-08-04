from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Candidatura(models.Model):
    ESTADO_CHOICES = [
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
        ('Cerrado', 'Cerrado'),
    ]

    nombre_lista = models.CharField(max_length=120)
    eslogan = models.CharField(max_length=255)
    presidente = models.CharField(max_length=120)
    foto_lista = models.ImageField(upload_to='candidatos/')
    plan_trabajo = models.FileField(
        upload_to='planes/',
        validators=[FileExtensionValidator(['pdf'])],
    )
    color_representativo = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Aprobada')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_lista


class Estudiante(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=30, unique=True)
    grado = models.CharField(max_length=30)
    paralelo = models.CharField(max_length=30)
    foto_credencial = models.ImageField(upload_to='estudiantes/')
    ha_votado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.cedula})"


class Voto(models.Model):
    eleccion = models.ForeignKey(Candidatura, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(default=timezone.now)
    hash_seguridad = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Voto {self.hash_seguridad} - {self.eleccion.nombre_lista}"
