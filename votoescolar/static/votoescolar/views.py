import csv
import hashlib
import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from .forms import CandidaturaForm, EstudianteForm, VotoForm, UserRegistrationForm
from .models import Candidatura, Estudiante, Voto
from django.utils import timezone


def is_tribunal(user):
    return user.is_staff or user.groups.filter(name='Tribunal Electoral').exists()


def is_estudiante(user):
    return user.groups.filter(name='Estudiante').exists()


@login_required
def dashboard(request):
    candidaturas = Candidatura.objects.all()
    estudiantes = Estudiante.objects.count()
    votos = Voto.objects.count()
    return render(request, 'elecciones/dashboard.html', {
        'candidaturas': candidaturas,
        'estudiantes': estudiantes,
        'votos': votos,
    })


@login_required
@user_passes_test(is_tribunal)
def candidatura_list(request):
    candidaturas = Candidatura.objects.all()
    return render(request, 'elecciones/candidatura_list.html', {'candidaturas': candidaturas})


@login_required
@user_passes_test(is_tribunal)
def candidatura_create(request):
    if request.method == 'POST':
        form = CandidaturaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidatura creada correctamente.')
            return redirect('votoescolar:candidatura_list')
    else:
        form = CandidaturaForm()
    return render(request, 'elecciones/candidatura_form.html', {'form': form, 'title': 'Nueva Candidatura'})


@login_required
@user_passes_test(is_tribunal)
def candidatura_update(request, pk):
    candidatura = get_object_or_404(Candidatura, pk=pk)
    if request.method == 'POST':
        form = CandidaturaForm(request.POST, request.FILES, instance=candidatura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidatura actualizada correctamente.')
            return redirect('votoescolar:candidatura_list')
    else:
        form = CandidaturaForm(instance=candidatura)
    return render(request, 'elecciones/candidatura_form.html', {'form': form, 'title': 'Editar Candidatura'})


@login_required
@user_passes_test(is_tribunal)
def candidatura_delete(request, pk):
    candidatura = get_object_or_404(Candidatura, pk=pk)
    if request.method == 'POST':
        candidatura.delete()
        messages.success(request, 'Candidatura eliminada correctamente.')
        return redirect('votoescolar:candidatura_list')
    return render(request, 'elecciones/candidatura_confirm_delete.html', {'candidatura': candidatura})


@login_required
@user_passes_test(is_tribunal)
def estudiante_list(request):
    estudiantes = Estudiante.objects.select_related('usuario').all()
    return render(request, 'elecciones/estudiante_list.html', {'estudiantes': estudiantes})


@login_required
@user_passes_test(is_tribunal)
def estudiante_create(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST, request.FILES)
        if form.is_valid():
            estudiante = form.save()
            messages.success(request, 'Estudiante creado correctamente.')
            return redirect('votoescolar:estudiante_list')
    else:
        form = EstudianteForm()
    return render(request, 'elecciones/estudiante_form.html', {'form': form, 'title': 'Nuevo Estudiante'})


@login_required
@user_passes_test(is_tribunal)
def estudiante_update(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, request.FILES, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante actualizado correctamente.')
            return redirect('votoescolar:estudiante_list')
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'elecciones/estudiante_form.html', {'form': form, 'title': 'Editar Estudiante'})


@login_required
@user_passes_test(is_tribunal)
def estudiante_delete(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, 'Estudiante eliminado correctamente.')
        return redirect('votoescolar:estudiante_list')
    return render(request, 'elecciones/estudiante_confirm_delete.html', {'estudiante': estudiante})


@login_required
def papeleta(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    if estudiante.ha_votado:
        messages.warning(request, 'Ya has votado. No puedes acceder a la papeleta otra vez.')
        return redirect('votoescolar:dashboard')

    candidaturas = Candidatura.objects.filter(estado='Aprobada')
    if request.method == 'POST':
        form = VotoForm(request.POST)
        if form.is_valid():
            candidatura = form.cleaned_data['eleccion']
            if candidatura.estado != 'Aprobada':
                messages.error(request, 'No se puede votar por una candidatura no aprobada.')
            else:
                voto = Voto(
                    eleccion=candidatura,
                    hash_seguridad=hashlib.sha256(f"{request.user.id}-{timezone.now().timestamp()}".encode()).hexdigest(),
                )
                voto.save()
                estudiante.ha_votado = True
                estudiante.save()
                self_hosted_url = request.build_absolute_uri('/')
                send_mail(
                    'Comprobante de su voto - VOTOESCOLAR',
                    f'Gracias por tu voto. Tu comprobante de verificación es: {voto.hash_seguridad}\nURL de verificación: {self_hosted_url}',
                    None,
                    [request.user.email],
                    fail_silently=True,
                )
                messages.success(request, 'Voto registrado. Se envió un comprobante por correo.')
                return redirect('votoescolar:voto_detail', pk=voto.pk)
    else:
        form = VotoForm()
    return render(request, 'elecciones/papeleta.html', {'form': form, 'candidaturas': candidaturas})


@login_required
def voto_detail(request, pk):
    voto = get_object_or_404(Voto, pk=pk)
    return render(request, 'elecciones/voto_detail.html', {'voto': voto})


@login_required
@user_passes_test(is_tribunal)
def resultados(request):
    candidaturas = Candidatura.objects.filter(estado='Aprobada')
    conteo = []
    for candidatura in candidaturas:
        conteo.append({
            'candidatura': candidatura,
            'votos': Voto.objects.filter(eleccion=candidatura).count()
        })
    ganador = max(conteo, key=lambda x: x['votos']) if conteo else None
    if request.method == 'POST' and 'cerrar_eleccion' in request.POST:
        for candidatura in candidaturas:
            candidatura.estado = 'Cerrado'
            candidatura.save()
        send_mail(
            'Resultados de la elección - VOTOESCOLAR',
            'Las elecciones han sido cerradas. Consulta el panel para los resultados oficiales.',
            None,
            [u.email for u in User.objects.filter(groups__name='Estudiante')],
            fail_silently=True,
        )
        messages.success(request, 'Elecciones cerradas y notificaciones enviadas.')
        return redirect('votoescolar:resultados')
    return render(request, 'elecciones/resultados.html', {'conteo': conteo, 'ganador': ganador})


@login_required
@user_passes_test(is_tribunal)
def export_padron_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="padron_electoral.csv"'
    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Email', 'Cédula', 'Grado', 'Paralelo', 'Ha votado'])
    for estudiante in Estudiante.objects.select_related('usuario').all():
        writer.writerow([
            estudiante.usuario.username,
            estudiante.usuario.email,
            estudiante.cedula,
            estudiante.grado,
            estudiante.paralelo,
            estudiante.ha_votado,
        ])
    return response


@login_required
@user_passes_test(is_tribunal)
def acta_final_pdf(request):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    candidaturas = Candidatura.objects.filter(estado='Cerrado')
    p.drawString(50, 750, 'Acta Final de VOTOESCOLAR')
    p.drawString(50, 730, f'Fecha: {timezone.now().strftime("%Y-%m-%d %H:%M")})')
    y = 700
    ganador = None
    max_votos = 0
    for candidatura in candidaturas:
        total = Voto.objects.filter(eleccion=candidatura).count()
        p.drawString(50, y, f'{candidatura.nombre_lista}: {total} votos')
        y -= 20
        if total > max_votos:
            max_votos = total
            ganador = candidatura
    if ganador:
        p.drawString(50, y - 20, f'Ganador: {ganador.nombre_lista}')
    p.drawString(50, y - 60, 'Firmas: ____________________________')
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='acta_final.pdf')
