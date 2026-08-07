from django.urls import path
from django.contrib.auth.models import User
from django.http import HttpResponse
from . import views

# Función temporal para recuperar el acceso a admin en Render
def reset_admin_secreto(request):
    try:
        u = User.objects.get(username='admin')
        u.set_password('Admin12345*')
        u.save()
        return HttpResponse("¡Éxito! Contraseña del usuario 'admin' cambiada a: Admin12345*")
    except User.DoesNotExist:
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin12345*')
        return HttpResponse("¡Éxito! El usuario 'admin' no existía pero fue creado con la clave: Admin12345*")

app_name = 'elecciones'

urlpatterns = [
    # Ruta temporal de emergencia
    path('reset-admin-secreto/', reset_admin_secreto, name='reset_admin_secreto'),

    # Panel Principal y Votación
    path('', views.dashboard, name='dashboard'),
    path('votar/', views.papeleta, name='papeleta'),
    path('confirmacion/<int:pk>/', views.confirmacion, name='confirmacion'),
    
    # Informes y Notificaciones Masivas
    path('acta/pdf/', views.acta_final_pdf, name='acta_final_pdf'),
    path('exportar/padron/', views.export_padron_excel, name='export_padron_excel'),
    path('exportar/padron/csv/', views.export_padron_csv, name='export_padron_csv'),
    path('notificar-resultados/', views.notificar_resultados_masivo, name='notificar_resultados_masivo'),
    
    # Control de Proceso y Sesión
    path('toggle-proceso/', views.toggle_proceso, name='toggle_proceso'),
    path('logout/', views.logout_view, name='logout_custom'),
    
    # Gestión Candidaturas
    path('candidaturas/', views.candidatura_list, name='candidatura_list'),
    path('candidaturas/nueva/', views.candidatura_create, name='candidatura_create'),
    path('candidaturas/<int:pk>/editar/', views.candidatura_update, name='candidatura_update'),
    path('candidaturas/<int:pk>/eliminar/', views.candidatura_delete, name='candidatura_delete'),
    
    # Gestión Estudiantes
    path('estudiantes/', views.estudiante_list, name='estudiante_list'),
    path('estudiantes/nuevo/', views.estudiante_create, name='estudiante_create'),
    path('estudiantes/<int:pk>/editar/', views.estudiante_update, name='estudiante_update'),
    path('estudiantes/<int:pk>/eliminar/', views.estudiante_delete, name='estudiante_delete'),
]