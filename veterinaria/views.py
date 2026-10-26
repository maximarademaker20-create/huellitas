import calendar
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import whatsapp
from .forms import (BajaForm, ConsultaForm, DuenoForm, EspecieForm, MascotaForm,
                    RazaForm, TurnoForm, VacunaAplicadaForm)
from .models import Dueno, Especie, Mascota, Recordatorio, Turno, VacunaAplicada


# ---------------------------------------------------------------------
# Inicio
# ---------------------------------------------------------------------
@login_required
def inicio(request):
    hoy = date.today()
    turnos_hoy = (Turno.objects.filter(fecha=hoy, estado='pendiente')
                  .select_related('mascota__dueno'))
    vacunas_proximas = (VacunaAplicada.objects
                        .filter(proxima_dosis__range=(hoy, hoy + timedelta(days=7)),
                                mascota__estado='activo')
                        .select_related('vacuna', 'mascota__dueno')
                        .order_by('proxima_dosis'))
    return render(request, 'veterinaria/inicio.html', {
        'hoy': hoy,
        'pacientes_activos': Mascota.objects.filter(estado='activo').count(),
        'turnos_hoy': turnos_hoy,
        'vacunas_proximas': vacunas_proximas,
    })


# ---------------------------------------------------------------------
# Mascotas
# ---------------------------------------------------------------------
@login_required
def mascotas(request):
    buscar = request.GET.get('q', '').strip()
    especie = request.GET.get('especie', '')
    estado = request.GET.get('estado', 'activo')

    lista = Mascota.objects.select_related('raza__especie', 'dueno')
    if buscar:
        lista = lista.filter(Q(nombre__icontains=buscar) | Q(dueno__nombre__icontains=buscar)
                             | Q(dueno__apellido__icontains=buscar) | Q(dueno__dni__icontains=buscar))
    if especie:
        lista = lista.filter(raza__especie_id=especie)
    if estado in ('activo', 'baja'):
        lista = lista.filter(estado=estado)

    return render(request, 'veterinaria/mascotas.html', {
        'mascotas': lista, 'especies': Especie.objects.all(),
        'buscar': buscar, 'especie': especie, 'estado': estado,
    })


@login_required
def mascota_form(request, pk=None):
    """Sirve para dar de alta una mascota nueva (sin pk) o editar una existente (con pk)."""
    mascota = get_object_or_404(Mascota, pk=pk) if pk else None
    inicial = {'dueno': request.GET.get('dueno')} if not pk else None
    form = MascotaForm(request.POST or None, instance=mascota, initial=inicial)
    if form.is_valid():
        mascota = form.save()
        messages.success(request, f'Se guardó la ficha de {mascota.nombre}.')
        return redirect('ficha', pk=mascota.pk)
    return render(request, 'veterinaria/mascota_form.html', {'form': form, 'mascota': mascota})


@login_required
def ficha(request, pk):
    mascota = get_object_or_404(Mascota.objects.select_related('raza__especie', 'dueno'), pk=pk)

    # Historial: consultas y vacunas juntas, de la más reciente a la más antigua
    historial = [{'tipo': 'consulta', 'fecha': c.fecha, 'obj': c} for c in mascota.consultas.all()]
    historial += [{'tipo': 'vacuna', 'fecha': v.fecha_aplicacion, 'obj': v}
                  for v in mascota.vacunas.select_related('vacuna')]
    historial.sort(key=lambda e: e['fecha'], reverse=True)

    return render(request, 'veterinaria/ficha.html', {
        'mascota': mascota, 'historial': historial, 'baja_form': BajaForm(),
    })


@login_required
@require_POST
def dar_baja(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    form = BajaForm(request.POST)
    if form.is_valid():
        mascota.estado = 'baja'
        mascota.fecha_baja = date.today()
        mascota.motivo_baja = form.cleaned_data['motivo']
        mascota.save()
        messages.success(request, f'{mascota.nombre} fue dada de baja. Su historial se conserva.')
    return redirect('ficha', pk=pk)


@login_required
@require_POST
def reactivar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    mascota.estado = 'activo'
    mascota.fecha_baja = None
    mascota.motivo_baja = ''
    mascota.save()
    messages.success(request, f'{mascota.nombre} volvió a estar activa.')
    return redirect('ficha', pk=pk)


@login_required
def nueva_consulta(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if mascota.estado == 'baja':
        messages.error(request, 'No se pueden registrar consultas de una mascota dada de baja.')
        return redirect('ficha', pk=pk)
    form = ConsultaForm(request.POST or None, initial={'fecha': date.today()})
    if form.is_valid():
        consulta = form.save(commit=False)
        consulta.mascota = mascota
        consulta.save()
        messages.success(request, 'Consulta guardada en el historial.')
        return redirect('ficha', pk=pk)
    return render(request, 'veterinaria/consulta_form.html', {'form': form, 'mascota': mascota})


@login_required
def registrar_vacuna(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if mascota.estado == 'baja':
        messages.error(request, 'No se pueden registrar vacunas de una mascota dada de baja.')
        return redirect('ficha', pk=pk)
    form = VacunaAplicadaForm(request.POST or None, initial={'fecha_aplicacion': date.today()})
    if form.is_valid():
        vacuna = form.save(commit=False)
        vacuna.mascota = mascota
        vacuna.save()
        messages.success(request, f'Vacuna {vacuna.vacuna} registrada.')
        return redirect('ficha', pk=pk)
    return render(request, 'veterinaria/vacuna_form.html', {'form': form, 'mascota': mascota})


# ---------------------------------------------------------------------
# Dueños
# ---------------------------------------------------------------------
@login_required
def duenos(request):
    buscar = request.GET.get('q', '').strip()
    lista = Dueno.objects.prefetch_related('mascotas')
    if buscar:
        lista = lista.filter(Q(nombre__icontains=buscar) | Q(apellido__icontains=buscar)
                             | Q(dni__icontains=buscar))
    return render(request, 'veterinaria/duenos.html', {'duenos': lista, 'buscar': buscar})


@login_required
def dueno_form(request, pk=None):
    """Sirve para registrar un dueño nuevo (sin pk) o editar uno existente (con pk)."""
    dueno = get_object_or_404(Dueno, pk=pk) if pk else None
    form = DuenoForm(request.POST or None, instance=dueno)
    if form.is_valid():
        dueno = form.save()
        messages.success(request, f'Se guardaron los datos de {dueno}.')
        # Si venía desde "Nueva mascota", vuelve ahí con el dueño ya elegido
        if request.GET.get('volver') == 'mascota':
            return redirect(f"{reverse('nueva_mascota')}?dueno={dueno.pk}")
        return redirect('duenos')
    return render(request, 'veterinaria/dueno_form.html', {'form': form, 'dueno': dueno})


# ---------------------------------------------------------------------
# Turnos
# ---------------------------------------------------------------------
@login_required
def turnos(request):
    try:
        dia = date.fromisoformat(request.GET.get('fecha', ''))
    except ValueError:
        dia = date.today()

    form = TurnoForm(request.POST or None, initial={'fecha': dia})
    if request.method == 'POST' and form.is_valid():
        try:
            turno = form.save()
        except IntegrityError:
            form.add_error('hora', 'Ya hay un turno a esa fecha y hora.')
        else:
            messages.success(request, f'Turno de {turno.mascota} guardado.')
            url = f"{reverse('turnos')}?fecha={turno.fecha:%Y-%m-%d}"
            if form.cleaned_data['enviar_recordatorio']:
                url += f'&avisar={turno.pk}'
            return redirect(url)

    # Calendario del mes que se está mirando
    dias_con_turnos = set(Turno.objects.filter(fecha__year=dia.year, fecha__month=dia.month,
                                               estado='pendiente').values_list('fecha', flat=True))
    semanas = calendar.Calendar(firstweekday=0).monthdatescalendar(dia.year, dia.month)
    mes_anterior = (dia.replace(day=1) - timedelta(days=1)).replace(day=1)
    mes_siguiente = (dia.replace(day=28) + timedelta(days=4)).replace(day=1)

    return render(request, 'veterinaria/turnos.html', {
        'dia': dia, 'hoy': date.today(), 'form': form, 'semanas': semanas,
        'dias_con_turnos': dias_con_turnos,
        'mes_anterior': mes_anterior, 'mes_siguiente': mes_siguiente,
        'turnos': (Turno.objects.filter(fecha=dia).exclude(estado='cancelado')
                   .select_related('mascota__dueno')),
        'avisar': request.GET.get('avisar'),
    })


@login_required
@require_POST
def cancelar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    turno.estado = 'cancelado'
    turno.save()
    messages.success(request, f'Se canceló el turno de {turno.mascota}.')
    return redirect(f"{reverse('turnos')}?fecha={turno.fecha:%Y-%m-%d}")


@login_required
@require_POST
def atender_turno(request, pk):
    """Marca el turno como atendido y abre directamente el formulario de consulta."""
    turno = get_object_or_404(Turno, pk=pk)
    turno.estado = 'atendido'
    turno.save()
    return redirect('nueva_consulta', pk=turno.mascota_id)


# ---------------------------------------------------------------------
# Recordatorios por WhatsApp
# Guardan el recordatorio en la base y abren WhatsApp con el mensaje escrito
# ---------------------------------------------------------------------
@login_required
def recordar_turno(request, pk):
    turno = get_object_or_404(Turno.objects.select_related('mascota__dueno'), pk=pk)
    Recordatorio.objects.create(tipo='turno', turno=turno, fecha_envio=timezone.now(), estado='enviado')
    return redirect(whatsapp.enlace(turno.mascota.dueno.telefono, whatsapp.mensaje_turno(turno)))


@login_required
def recordar_vacuna(request, pk):
    vacuna = get_object_or_404(VacunaAplicada.objects.select_related('mascota__dueno', 'vacuna'), pk=pk)
    Recordatorio.objects.create(tipo='vacuna', vacuna_aplicada=vacuna, fecha_envio=timezone.now(), estado='enviado')
    return redirect(whatsapp.enlace(vacuna.mascota.dueno.telefono, whatsapp.mensaje_vacuna(vacuna)))


# ---------------------------------------------------------------------
# Especies y razas
# ---------------------------------------------------------------------
@login_required
def especies(request):
    especie_form = EspecieForm(prefix='especie')
    raza_form = RazaForm(prefix='raza')
    if request.method == 'POST':
        if 'agregar_especie' in request.POST:
            especie_form = EspecieForm(request.POST, prefix='especie')
            if especie_form.is_valid():
                especie_form.save()
                messages.success(request, 'Especie agregada.')
                return redirect('especies')
        else:
            raza_form = RazaForm(request.POST, prefix='raza')
            if raza_form.is_valid():
                raza_form.save()
                messages.success(request, 'Raza agregada.')
                return redirect('especies')
    return render(request, 'veterinaria/especies.html', {
        'especies': Especie.objects.prefetch_related('razas'),
        'especie_form': especie_form, 'raza_form': raza_form,
    })
