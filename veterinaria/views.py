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


@login_required
def inicio(request):
    hoy = date.today()
    turnos_hoy = Turno.objects.filter(fecha=hoy, estado="pendiente").select_related("mascota__dueno")
    vacunas_proximas = (VacunaAplicada.objects
                        .filter(proxima_dosis__range=(hoy, hoy + timedelta(days=7)), mascota__estado="activo")
                        .select_related("vacuna", "mascota__dueno")
                        .order_by("proxima_dosis"))
    datos = {
        "hoy": hoy,
        "pacientes_activos": Mascota.objects.filter(estado="activo").count(),
        "turnos_hoy": turnos_hoy,
        "vacunas_proximas": vacunas_proximas,
    }
    return render(request, "veterinaria/inicio.html", datos)


@login_required
def mascotas(request):
    buscar = request.GET.get("buscar", "")
    especie = request.GET.get("especie", "")
    estado = request.GET.get("estado", "activo")

    lista_mascotas = Mascota.objects.select_related("raza__especie", "dueno")
    if buscar != "":
        lista_mascotas = lista_mascotas.filter(
            Q(nombre__icontains=buscar)
            | Q(dueno__nombre__icontains=buscar)
            | Q(dueno__apellido__icontains=buscar)
            | Q(dueno__dni__icontains=buscar)
        )
    if especie != "":
        lista_mascotas = lista_mascotas.filter(raza__especie_id=especie)
    if estado == "activo" or estado == "baja":
        lista_mascotas = lista_mascotas.filter(estado=estado)

    datos = {
        "mascotas": lista_mascotas,
        "especies": Especie.objects.all(),
        "buscar": buscar,
        "especie": especie,
        "estado": estado,
    }
    return render(request, "veterinaria/mascotas.html", datos)


@login_required
def mascota_form(request, pk=None):
    mascota = get_object_or_404(Mascota, pk=pk) if pk else None
    dueno_elegido = request.GET.get("dueno")
    inicial = {"dueno": dueno_elegido} if mascota is None else None
    form = MascotaForm(request.POST or None, instance=mascota, initial=inicial)
    if request.method == "POST" and form.is_valid():
        mascota = form.save()
        messages.success(request, f"Se guardó la ficha de {mascota.nombre}.")
        return redirect("ficha", pk=mascota.pk)
    datos = {"form": form, "mascota": mascota}
    return render(request, "veterinaria/mascota_form.html", datos)


@login_required
def ficha(request, pk):
    mascota = get_object_or_404(Mascota.objects.select_related("raza__especie", "dueno"), pk=pk)
    datos = {
        "mascota": mascota,
        "historial": mascota.historial(),
        "baja_form": BajaForm(),
    }
    return render(request, "veterinaria/ficha.html", datos)


@login_required
@require_POST
def dar_baja(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    form = BajaForm(request.POST)
    if form.is_valid():
        mascota.dar_de_baja(form.cleaned_data["motivo"])
        messages.success(request, f"{mascota.nombre} fue dada de baja. Su historial se conserva.")
    return redirect("ficha", pk=pk)


@login_required
@require_POST
def reactivar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    mascota.reactivar()
    messages.success(request, f"{mascota.nombre} volvió a estar activa.")
    return redirect("ficha", pk=pk)


@login_required
def nueva_consulta(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if mascota.estado == "baja":
        messages.error(request, "No se pueden registrar consultas de una mascota dada de baja.")
        return redirect("ficha", pk=pk)
    form = ConsultaForm(request.POST or None, initial={"fecha": date.today()})
    if request.method == "POST" and form.is_valid():
        consulta = form.save(commit=False)
        consulta.mascota = mascota
        consulta.save()
        messages.success(request, "Consulta guardada en el historial.")
        return redirect("ficha", pk=pk)
    datos = {"form": form, "mascota": mascota}
    return render(request, "veterinaria/consulta_form.html", datos)


@login_required
def registrar_vacuna(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if mascota.estado == "baja":
        messages.error(request, "No se pueden registrar vacunas de una mascota dada de baja.")
        return redirect("ficha", pk=pk)
    form = VacunaAplicadaForm(request.POST or None, initial={"fecha_aplicacion": date.today()})
    if request.method == "POST" and form.is_valid():
        vacuna = form.save(commit=False)
        vacuna.mascota = mascota
        vacuna.save()
        messages.success(request, f"Vacuna {vacuna.vacuna} registrada.")
        return redirect("ficha", pk=pk)
    datos = {"form": form, "mascota": mascota}
    return render(request, "veterinaria/vacuna_form.html", datos)


@login_required
def duenos(request):
    buscar = request.GET.get("buscar", "")

    lista_duenos = Dueno.objects.prefetch_related("mascotas")
    if buscar != "":
        lista_duenos = lista_duenos.filter(
            Q(nombre__icontains=buscar)
            | Q(apellido__icontains=buscar)
            | Q(dni__icontains=buscar)
        )

    datos = {"duenos": lista_duenos, "buscar": buscar}
    return render(request, "veterinaria/duenos.html", datos)


@login_required
def dueno_form(request, pk=None):
    dueno = get_object_or_404(Dueno, pk=pk) if pk else None
    volver = request.GET.get("volver")
    form = DuenoForm(request.POST or None, instance=dueno)

    if request.method == "POST":
        print(">>> Llegó un POST para guardar un dueño")
        print("    Datos recibidos:", request.POST.get("nombre"), request.POST.get("apellido"),
              "- DNI", request.POST.get("dni"))
        if form.is_valid():
            dueno = form.save()
            print(f">>> Dueño guardado en MySQL con id {dueno.pk}")
            messages.success(request, f"Se guardaron los datos de {dueno}.")
            if volver == "mascota":
                return redirect(f"{reverse('nueva_mascota')}?dueno={dueno.pk}")
            return redirect("duenos")
        print(">>> No se guardó, hay errores:", form.errors.as_text())

    datos = {"form": form, "dueno": dueno}
    return render(request, "veterinaria/dueno_form.html", datos)


@login_required
def turnos(request):
    fecha = request.GET.get("fecha", "")
    avisar = request.GET.get("avisar")
    try:
        dia = date.fromisoformat(fecha)
    except ValueError:
        dia = date.today()

    form = TurnoForm(request.POST or None, initial={"fecha": dia})
    if request.method == "POST" and form.is_valid():
        try:
            turno = form.save()
        except IntegrityError:
            form.add_error("hora", "Ya hay un turno a esa fecha y hora.")
        else:
            messages.success(request, f"Turno de {turno.mascota} guardado.")
            url = f"{reverse('turnos')}?fecha={turno.fecha:%Y-%m-%d}"
            if form.cleaned_data["enviar_recordatorio"]:
                url += f"&avisar={turno.pk}"
            return redirect(url)

    dias_con_turnos = set(Turno.objects.filter(fecha__year=dia.year, fecha__month=dia.month,
                                               estado="pendiente").values_list("fecha", flat=True))
    turnos_del_dia = Turno.objects.filter(fecha=dia).exclude(estado="cancelado").select_related("mascota__dueno")

    datos = {
        "dia": dia,
        "hoy": date.today(),
        "form": form,
        "semanas": calendar.Calendar(firstweekday=0).monthdatescalendar(dia.year, dia.month),
        "dias_con_turnos": dias_con_turnos,
        "mes_anterior": (dia.replace(day=1) - timedelta(days=1)).replace(day=1),
        "mes_siguiente": (dia.replace(day=28) + timedelta(days=4)).replace(day=1),
        "turnos": turnos_del_dia,
        "avisar": avisar,
    }
    return render(request, "veterinaria/turnos.html", datos)


@login_required
@require_POST
def cancelar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    turno.estado = "cancelado"
    turno.save()
    messages.success(request, f"Se canceló el turno de {turno.mascota}.")
    return redirect(f"{reverse('turnos')}?fecha={turno.fecha:%Y-%m-%d}")


@login_required
@require_POST
def atender_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    turno.estado = "atendido"
    turno.save()
    return redirect("nueva_consulta", pk=turno.mascota_id)


@login_required
def recordar_turno(request, pk):
    turno = get_object_or_404(Turno.objects.select_related("mascota__dueno"), pk=pk)
    Recordatorio.objects.create(tipo="turno", turno=turno, fecha_envio=timezone.now(), estado="enviado")
    return redirect(whatsapp.enlace(turno.mascota.dueno.telefono, whatsapp.mensaje_turno(turno)))


@login_required
def recordar_vacuna(request, pk):
    vacuna = get_object_or_404(VacunaAplicada.objects.select_related("mascota__dueno", "vacuna"), pk=pk)
    Recordatorio.objects.create(tipo="vacuna", vacuna_aplicada=vacuna, fecha_envio=timezone.now(), estado="enviado")
    return redirect(whatsapp.enlace(vacuna.mascota.dueno.telefono, whatsapp.mensaje_vacuna(vacuna)))


@login_required
def especies(request):
    especie_form = EspecieForm(prefix="especie")
    raza_form = RazaForm(prefix="raza")
    if request.method == "POST":
        if "agregar_especie" in request.POST:
            especie_form = EspecieForm(request.POST, prefix="especie")
            if especie_form.is_valid():
                especie_form.save()
                messages.success(request, "Especie agregada.")
                return redirect("especies")
        else:
            raza_form = RazaForm(request.POST, prefix="raza")
            if raza_form.is_valid():
                raza_form.save()
                messages.success(request, "Raza agregada.")
                return redirect("especies")
    datos = {
        "especies": Especie.objects.prefetch_related("razas"),
        "especie_form": especie_form,
        "raza_form": raza_form,
    }
    return render(request, "veterinaria/especies.html", datos)
