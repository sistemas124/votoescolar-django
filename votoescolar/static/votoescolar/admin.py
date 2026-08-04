from django.contrib import admin
from .models import Candidatura, Estudiante, Voto


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre_lista', 'presidente', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('nombre_lista', 'presidente', 'eslogan')


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cedula', 'grado', 'paralelo', 'ha_votado')
    search_fields = ('usuario__username', 'cedula')
    list_filter = ('grado', 'paralelo', 'ha_votado')


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('eleccion', 'fecha_hora', 'hash_seguridad')
    search_fields = ('hash_seguridad', 'eleccion__nombre_lista')
