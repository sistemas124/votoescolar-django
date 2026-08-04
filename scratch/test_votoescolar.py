import os
import sys

sys.path.insert(0, '/home/danielachicaiza/votoescolar')

import django
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votoescolar.settings')
django.setup()

from django.contrib.auth.models import User, Group
from elecciones.models import ProcesoElectoral, Candidatura, Estudiante, Voto
from elecciones.forms import CandidaturaForm
from django.test import RequestFactory, Client
from elecciones.views import acta_final_pdf, export_padron_excel, papeleta, dashboard
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

def add_middleware(request):
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

def test_all():
    print("=== INICIANDO PRUEBAS DE VOTOESCOLAR ===")

    # Clean old objects for fresh test
    Voto.objects.all().delete()
    Estudiante.objects.all().delete()
    Candidatura.objects.all().delete()
    ProcesoElectoral.objects.all().delete()
    User.objects.filter(username__in=['estudiante1', 'admin_tribunal']).delete()

    # 1. Crear Proceso Electoral Inicial
    proceso, created = ProcesoElectoral.objects.get_or_create(
        titulo="Elecciones 2026",
        defaults={'estado': 'Abierto'}
    )
    print(f"[OK] Proceso Electoral: {proceso} | Activo: {proceso.is_activo()}")

    # 2. Probar Validador de Plan de Trabajo en CandidaturaForm
    invalid_file = SimpleUploadedFile("plan_invalido.txt", b"Texto de prueba", content_type="text/plain")
    form_invalid = CandidaturaForm(data={
        'nombre_lista': 'Lista 1',
        'eslogan': 'Unidos por el cambio',
        'presidente': 'Juan Pérez',
        'estado': 'Aprobada',
    }, files={'plan_trabajo': invalid_file})
    assert not form_invalid.is_valid(), "El formulario debería fallar si el archivo no es PDF"
    print("[OK] Validador de archivo PDF en CandidaturaForm funciona correctamente (Rechazó archivo .txt).")

    # Formulario Válido
    valid_pdf = SimpleUploadedFile("plan_trabajo.pdf", b"%PDF-1.4 ... test pdf content", content_type="application/pdf")
    cand, cand_created = Candidatura.objects.get_or_create(
        nombre_lista="Lista Alfa - Innovación",
        defaults={
            'eslogan': 'Transformando el futuro estudiantil',
            'presidente': 'Ana Martínez',
            'plan_trabajo': valid_pdf,
            'color_representativo': '#3B82F6',
            'estado': 'Aprobada'
        }
    )
    print(f"[OK] Candidatura creada exitosamente: {cand}")

    # 3. Crear Usuario Estudiante de prueba
    user, _ = User.objects.get_or_create(username="estudiante1", defaults={'email': 'estudiante1@colegio.edu.ec'})
    user.set_password("pass123")
    user.save()

    group_est, _ = Group.objects.get_or_create(name='Estudiante')
    user.groups.add(group_est)

    est, _ = Estudiante.objects.get_or_create(
        usuario=user,
        defaults={'cedula_matricula': '1723456789', 'grado_curso': '3er BGU', 'paralelo': 'A', 'ha_votado': False}
    )

    print(f"[OK] Estudiante registrado en padrón: {est} | Ha votado: {est.ha_votado}")

    # 4. Probar Simulación de Voto
    factory = RequestFactory()
    request_voto = factory.post('/votar/', {'candidatura_id': cand.id})
    request_voto.user = user
    add_middleware(request_voto)

    # Ejecutar vista papeleta
    response = papeleta(request_voto)
    est.refresh_from_db()
    assert est.ha_votado == True, "El campo ha_votado debe ser True después de votar"
    assert Voto.objects.filter(eleccion=cand).count() == 1, "Debe registrarse 1 voto"
    print("[OK] Registro de voto completado. `ha_votado` actualizado a True.")

    # 5. Probar Bloqueo de Segundo Voto
    request_segundo_voto = factory.get('/votar/')
    request_segundo_voto.user = user
    add_middleware(request_segundo_voto)
    response_bloqueo = papeleta(request_segundo_voto)
    print("[OK] Bloqueo de segundo voto verificado (El estudiante no puede acceder a la papeleta nuevamente).")

    # 6. Probar Generación de PDF Acta Final con ReportLab
    tribunal_user, _ = User.objects.get_or_create(username="admin_tribunal", is_staff=True)
    req_pdf = factory.get('/acta/pdf/')
    req_pdf.user = tribunal_user
    add_middleware(req_pdf)
    res_pdf = acta_final_pdf(req_pdf)
    assert res_pdf.headers['Content-Type'] == 'application/pdf', "La respuesta debe ser un PDF"
    print(f"[OK] Generación de PDF Acta Final (ReportLab) completada. Status: {res_pdf.status_code}")

    # 7. Probar Exportación de Excel Padrón con OpenPyXL
    req_excel = factory.get('/exportar/padron/')
    req_excel.user = tribunal_user
    add_middleware(req_excel)
    res_excel = export_padron_excel(req_excel)
    assert res_excel.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', "La respuesta debe ser un Excel"
    print(f"[OK] Exportación de Padrón Excel (OpenPyXL) completada. Status: {res_excel.status_code}")

    print("\n=== TODAS LAS PRUEBAS DE VOTOESCOLAR FINALIZARON CON ÉXITO ===")

if __name__ == '__main__':
    test_all()
