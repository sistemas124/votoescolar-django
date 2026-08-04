from django.contrib import admin
from .models import ProcesoElectoral, Candidatura, Estudiante, Voto


@admin.register(ProcesoElectoral)
class ProcesoElectoralAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'estado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado',)
    search_fields = ('titulo',)


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre_lista', 'presidente', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('nombre_lista', 'presidente', 'eslogan')


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cedula_matricula', 'grado_curso', 'paralelo', 'ha_votado')
    list_filter = ('ha_votado', 'grado_curso', 'paralelo')
    search_fields = ('cedula_matricula', 'usuario__username', 'usuario__first_name', 'usuario__last_name')


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('eleccion', 'fecha_hora', 'hash_seguridad')
    list_filter = ('eleccion', 'fecha_hora')
    search_fields = ('hash_seguridad', 'eleccion__nombre_lista')
