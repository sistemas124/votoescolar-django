from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class ProcesoElectoral(models.Model):
    ESTADO_CHOICES = [
        ('Abierto', 'Abierto'),
        ('Cerrado', 'Cerrado'),
    ]

    titulo = models.CharField(max_length=150, default="Elecciones Estudiantiles")
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Abierto')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Proceso Electoral"
        verbose_name_plural = "Procesos Electorales"

    def __str__(self):
        return f"{self.titulo} - {self.estado}"

    def is_activo(self):
        if self.estado != 'Abierto':
            return False
        now = timezone.now()
        if self.fecha_inicio and now < self.fecha_inicio:
            return False
        if self.fecha_fin and now > self.fecha_fin:
            return False
        return True


class Candidatura(models.Model):
    ESTADO_CHOICES = [
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
        ('Cerrado', 'Cerrado'),
    ]

    nombre_lista = models.CharField(max_length=120)
    eslogan = models.CharField(max_length=255)
    presidente = models.CharField(max_length=120)
    foto_lista = models.ImageField(upload_to='candidatos/', blank=True, null=True)
    plan_trabajo = models.FileField(
        upload_to='planes/',
        validators=[FileExtensionValidator(['pdf'])],
    )
    color_representativo = models.CharField(max_length=20, blank=True, null=True, default="#3B82F6")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Aprobada')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_lista


class Estudiante(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='estudiante_profile')
    cedula_matricula = models.CharField(max_length=30, unique=True)
    grado_curso = models.CharField(max_length=30)
    paralelo = models.CharField(max_length=30)
    foto_credencial = models.ImageField(upload_to='estudiantes/', blank=True, null=True)
    ha_votado = models.BooleanField(default=False)

    @property
    def cedula(self):
        return self.cedula_matricula

    @property
    def grado(self):
        return self.grado_curso

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.cedula_matricula})"


class Voto(models.Model):
    # NOTA: Voto no posee relación directa con Estudiante para garantizar el voto secreto
    eleccion = models.ForeignKey(Candidatura, on_delete=models.CASCADE, related_name='votos')
    fecha_hora = models.DateTimeField(default=timezone.now)
    hash_seguridad = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Voto {self.hash_seguridad[:8]} - {self.eleccion.nombre_lista}"
