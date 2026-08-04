from django.urls import path
from . import views

app_name = 'votoescolar'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('candidaturas/', views.candidatura_list, name='candidatura_list'),
    path('candidaturas/nueva/', views.candidatura_create, name='candidatura_create'),
    path('candidaturas/<int:pk>/editar/', views.candidatura_update, name='candidatura_update'),
    path('candidaturas/<int:pk>/eliminar/', views.candidatura_delete, name='candidatura_delete'),
    path('estudiantes/', views.estudiante_list, name='estudiante_list'),
    path('estudiantes/nuevo/', views.estudiante_create, name='estudiante_create'),
    path('estudiantes/<int:pk>/editar/', views.estudiante_update, name='estudiante_update'),
    path('estudiantes/<int:pk>/eliminar/', views.estudiante_delete, name='estudiante_delete'),
    path('votar/', views.papeleta, name='papeleta'),
    path('voto/<int:pk>/', views.voto_detail, name='voto_detail'),
    path('resultados/', views.resultados, name='resultados'),
    path('exportar/padron/', views.export_padron_csv, name='export_padron_csv'),
    path('acta/pdf/', views.acta_final_pdf, name='acta_final_pdf'),
]
