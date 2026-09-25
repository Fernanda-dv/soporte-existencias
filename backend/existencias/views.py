import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction, IntegrityError
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from catalogos.models import (
    Direccion, Departamento, Cargo, TipoEquipo,
    MemoriaRAM, Disco, Procesador, SistemaOperativo,
    PulgadasMonitor, TipoImpresora, EstadoImpresora
)
from .models import Equipo, Monitor, Funcionario, ImpresoraRegistro


def es_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
def ingresar_equipo(request):
    if request.method == 'POST':
        nombre_func = request.POST.get('funcionario_nombre', '').strip().upper()
        direccion_id = request.POST.get('direccion')
        departamento_id = request.POST.get('departamento')
        anexo_val = request.POST.get('anexo', '').strip()
        cargo_id = request.POST.get('cargo')

        tipo_equipo_id = request.POST.get('tipo_equipo')
        num_serie = request.POST.get('numero_serie', '').strip() or None
        num_inventario = request.POST.get('numero_inventario', '').strip() or None

        # Validación: Obligatorio al menos uno de los dos
        if not num_serie and not num_inventario:
            messages.error(request, "Debe ingresar al menos el Número de Serie o el Número de Inventario.")
        elif num_serie and Equipo.objects.filter(numero_serie=num_serie).exists():
            messages.error(request, f"El N° de Serie '{num_serie}' ya está registrado.")
        elif num_inventario and Equipo.objects.filter(numero_inventario=num_inventario).exists():
            messages.error(request, f"El N° de Inventario '{num_inventario}' ya está registrado.")
        else:
            try:
                ram_id = request.POST.get('ram')
                disco_id = request.POST.get('disco')
                procesador_id = request.POST.get('procesador')
                so_id = request.POST.get('sistema_operativo')

                tiene_monitor = request.POST.get('tiene_monitor') == 'si'
                cant_monitores = int(request.POST.get('cantidad_monitores', 0)) if tiene_monitor else 0
                tiene_impresora = request.POST.get('tiene_impresora') == 'si'
                tipo_impresora_id = request.POST.get('tipo_impresora') if tiene_impresora else None

                with transaction.atomic():
                    funcionario = Funcionario.objects.create(
                        nombre=nombre_func, direccion_id=direccion_id,
                        departamento_id=departamento_id, anexo=anexo_val, cargo_id=cargo_id
                    )
                    equipo = Equipo.objects.create(
                        funcionario=funcionario, tipo_id=tipo_equipo_id,
                        numero_serie=num_serie, numero_inventario=num_inventario,
                        ram_id=ram_id, disco_id=disco_id,
                        procesador_id=procesador_id, sistema_operativo_id=so_id,
                        tiene_monitor=tiene_monitor, tiene_impresora=tiene_impresora,
                        tipo_impresora_id=tipo_impresora_id, tecnico=request.user
                    )
                    if tiene_monitor:
                        if cant_monitores >= 1 and request.POST.get('monitor1_pulgadas'):
                            Monitor.objects.create(
                                equipo=equipo, pantalla_numero=1,
                                pulgadas_id=request.POST.get('monitor1_pulgadas'),
                                hdmi=request.POST.get('monitor1_hdmi') in ['True', 'on', 'true']
                            )
                        if cant_monitores == 2 and request.POST.get('monitor2_pulgadas'):
                            Monitor.objects.create(
                                equipo=equipo, pantalla_numero=2,
                                pulgadas_id=request.POST.get('monitor2_pulgadas'),
                                hdmi=request.POST.get('monitor2_hdmi') in ['True', 'on', 'true']
                            )
                return redirect('ver_equipos')
            except IntegrityError:
                messages.error(request, "Ocurrió un error al registrar el equipo.")

    context = {
        'direcciones': Direccion.objects.all(), 'departamentos': Departamento.objects.all(),
        'cargos': Cargo.objects.all(), 'tipos_equipo': TipoEquipo.objects.all(),
        'rams': MemoriaRAM.objects.all(), 'discos': Disco.objects.all(),
        'procesadores': Procesador.objects.all(), 'sistemas_operativos': SistemaOperativo.objects.all(),
        'pulgadas_monitor': PulgadasMonitor.objects.all(), 'tipos_impresora': TipoImpresora.objects.all(),
    }
    return render(request, 'form.html', context)


@login_required
def ver_equipos(request):
    filtro_tecnico = request.GET.get('tecnico', 'todos')
    query_busqueda = request.GET.get('q', '').strip()

    equipos = Equipo.objects.select_related(
        'funcionario', 'funcionario__direccion', 'funcionario__departamento', 'funcionario__cargo',
        'tipo', 'ram', 'disco', 'procesador', 'sistema_operativo',
        'tipo_impresora', 'tecnico'
    ).prefetch_related('monitores').order_by('-fecha_creacion')

    impresoras = ImpresoraRegistro.objects.select_related(
        'direccion', 'departamento', 'tipo_impresora', 'estado', 'tecnico'
    ).order_by('-fecha_creacion')

    if filtro_tecnico == 'mio':
        equipos = equipos.filter(tecnico=request.user)
        impresoras = impresoras.filter(tecnico=request.user)

    if query_busqueda:
        equipos = equipos.filter(
            funcionario__nombre__icontains=query_busqueda
        ) | equipos.filter(
            numero_serie__icontains=query_busqueda
        ) | equipos.filter(
            numero_inventario__icontains=query_busqueda
        )

        impresoras = impresoras.filter(
            departamento__nombre__icontains=query_busqueda
        ) | impresoras.filter(
            tipo_impresora__nombre__icontains=query_busqueda
        )

    context = {
        'equipos': equipos,
        'impresoras': impresoras,
        'filtro_tecnico': filtro_tecnico,
        'query_busqueda': query_busqueda,
        'es_admin': es_admin(request.user),
    }
    return render(request, 'tabla.html', context)


@login_required
def editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    funcionario = equipo.funcionario

    if request.method == 'POST':
        with transaction.atomic():
            funcionario.nombre = request.POST.get('funcionario_nombre', '').strip().upper()
            funcionario.direccion_id = request.POST.get('direccion')
            funcionario.departamento_id = request.POST.get('departamento')
            funcionario.anexo = request.POST.get('anexo', '').strip()
            funcionario.cargo_id = request.POST.get('cargo')
            funcionario.save()

            equipo.tipo_id = request.POST.get('tipo_equipo')
            equipo.numero_serie = request.POST.get('numero_serie', '').strip() or None
            equipo.numero_inventario = request.POST.get('numero_inventario', '').strip() or None
            equipo.ram_id = request.POST.get('ram')
            equipo.disco_id = request.POST.get('disco')
            equipo.procesador_id = request.POST.get('procesador')
            equipo.sistema_operativo_id = request.POST.get('sistema_operativo')

            tiene_monitor = request.POST.get('tiene_monitor') == 'si'
            tiene_impresora = request.POST.get('tiene_impresora') == 'si'
            equipo.tiene_monitor = tiene_monitor
            equipo.tiene_impresora = tiene_impresora
            equipo.tipo_impresora_id = request.POST.get('tipo_impresora') if tiene_impresora else None
            equipo.save()

            equipo.monitores.all().delete()
            if tiene_monitor:
                cant_monitores = int(request.POST.get('cantidad_monitores', 0))
                if cant_monitores >= 1 and request.POST.get('monitor1_pulgadas'):
                    Monitor.objects.create(
                        equipo=equipo, pantalla_numero=1,
                        pulgadas_id=request.POST.get('monitor1_pulgadas'),
                        hdmi=request.POST.get('monitor1_hdmi') in ['True', 'on', 'true']
                    )
                if cant_monitores == 2 and request.POST.get('monitor2_pulgadas'):
                    Monitor.objects.create(
                        equipo=equipo, pantalla_numero=2,
                        pulgadas_id=request.POST.get('monitor2_pulgadas'),
                        hdmi=request.POST.get('monitor2_hdmi') in ['True', 'on', 'true']
                    )
        return redirect('ver_equipos')

    # Monitores asociados
    monitor1 = equipo.monitores.filter(pantalla_numero=1).first()
    monitor2 = equipo.monitores.filter(pantalla_numero=2).first()

    context = {
        'equipo': equipo,
        'funcionario': funcionario,
        'monitor1': monitor1,
        'monitor2': monitor2,
        'direcciones': Direccion.objects.all(),
        'departamentos': Departamento.objects.all(),
        'cargos': Cargo.objects.all(),
        'tipos_equipo': TipoEquipo.objects.all(),
        'rams': MemoriaRAM.objects.all(),
        'discos': Disco.objects.all(),
        'procesadores': Procesador.objects.all(),
        'sistemas_operativos': SistemaOperativo.objects.all(),
        'pulgadas_monitor': PulgadasMonitor.objects.all(),
        'tipos_impresora': TipoImpresora.objects.all(),
    }
    return render(request, 'form.html', context)


@login_required
def exportar_excel(request):
    filtro_tecnico = request.GET.get('tecnico', 'todos')
    query_busqueda = request.GET.get('q', '').strip()

    equipos = Equipo.objects.select_related(
        'funcionario', 'funcionario__direccion', 'funcionario__departamento', 'funcionario__cargo',
        'tipo', 'ram', 'disco', 'procesador', 'sistema_operativo',
        'tipo_impresora', 'tecnico'
    ).prefetch_related('monitores').order_by('-fecha_creacion')

    if filtro_tecnico == 'mio':
        equipos = equipos.filter(tecnico=request.user)

    if query_busqueda:
        equipos = equipos.filter(
            funcionario__nombre__icontains=query_busqueda
        ) | equipos.filter(
            numero_serie__icontains=query_busqueda
        ) | equipos.filter(
            numero_inventario__icontains=query_busqueda
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario de Equipos"

    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='10174A', end_color='10174A', fill_type='solid')

    headers = [
        "Funcionario", "Dirección", "Departamento", "Anexo", "Cargo",
        "Tipo Equipo", "N° Serie", "N° Inventario", "RAM", "Disco", "Procesador", "Sistema Operativo",
        "¿Tiene Monitor?", "Cant. Monitores", "Detalle Monitores",
        "¿Tiene Impresora?", "Tipo Impresora", "Fecha Creación", "Técnico Registrador"
    ]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for eq in equipos:
        monitores = list(eq.monitores.all())
        cant_mon = len(monitores)
        detalle_mon = " / ".join([f"Pantalla {m.pantalla_numero}: {m.pulgadas.tipo} (HDMI: {'Sí' if m.hdmi else 'No'})" for m in monitores]) if cant_mon > 0 else "N/A"

        ws.append([
            eq.funcionario.nombre,
            eq.funcionario.direccion.nombre,
            eq.funcionario.departamento.nombre,
            eq.funcionario.anexo,
            eq.funcionario.cargo.nombre,
            eq.tipo.nombre,
            eq.numero_serie or "N/A",
            eq.numero_inventario or "N/A",
            eq.ram.tipo,
            eq.disco.tipo,
            eq.procesador.nombre,
            eq.sistema_operativo.tipo,
            "Sí" if eq.tiene_monitor else "No",
            cant_mon if eq.tiene_monitor else 0,
            detalle_mon,
            "Sí" if eq.tiene_impresora else "No",
            eq.tipo_impresora.nombre if eq.tiene_impresora and eq.tipo_impresora else "N/A",
            eq.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            eq.tecnico.get_full_name() or eq.tecnico.username
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventario_equipos_maipu.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_csv(request):
    filtro_tecnico = request.GET.get('tecnico', 'todos')
    query_busqueda = request.GET.get('q', '').strip()

    equipos = Equipo.objects.select_related(
        'funcionario', 'funcionario__direccion', 'funcionario__departamento', 'funcionario__cargo',
        'tipo', 'ram', 'disco', 'procesador', 'sistema_operativo',
        'tipo_impresora', 'tecnico'
    ).prefetch_related('monitores').order_by('-fecha_creacion')

    if filtro_tecnico == 'mio':
        equipos = equipos.filter(tecnico=request.user)

    if query_busqueda:
        equipos = equipos.filter(
            funcionario__nombre__icontains=query_busqueda
        ) | equipos.filter(
            numero_serie__icontains=query_busqueda
        ) | equipos.filter(
            numero_inventario__icontains=query_busqueda
        )

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="inventario_equipos_maipu.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        "Funcionario", "Dirección", "Departamento", "Anexo", "Cargo",
        "Tipo Equipo", "N° Serie", "N° Inventario", "RAM", "Disco", "Procesador", "Sistema Operativo",
        "¿Tiene Monitor?", "Cant. Monitores", "Detalle Monitores",
        "¿Tiene Impresora?", "Tipo Impresora", "Fecha Creación", "Técnico Registrador"
    ])

    for eq in equipos:
        monitores = list(eq.monitores.all())
        cant_mon = len(monitores)
        detalle_mon = " / ".join([f"Pantalla {m.pantalla_numero}: {m.pulgadas.tipo} (HDMI: {'Sí' if m.hdmi else 'No'})" for m in monitores]) if cant_mon > 0 else "N/A"

        writer.writerow([
            eq.funcionario.nombre,
            eq.funcionario.direccion.nombre,
            eq.funcionario.departamento.nombre,
            eq.funcionario.anexo,
            eq.funcionario.cargo.nombre,
            eq.tipo.nombre,
            eq.numero_serie or "N/A",
            eq.numero_inventario or "N/A",
            eq.ram.tipo,
            eq.disco.tipo,
            eq.procesador.nombre,
            eq.sistema_operativo.tipo,
            "Sí" if eq.tiene_monitor else "No",
            cant_mon if eq.tiene_monitor else 0,
            detalle_mon,
            "Sí" if eq.tiene_impresora else "No",
            eq.tipo_impresora.nombre if eq.tiene_impresora and eq.tipo_impresora else "N/A",
            eq.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            eq.tecnico.get_full_name() or eq.tecnico.username
        ])

    return response


@login_required
def ingresar_impresora(request):
    if request.method == 'POST':
        ImpresoraRegistro.objects.create(
            direccion_id=request.POST.get('direccion'),
            departamento_id=request.POST.get('departamento'),
            tipo_impresora_id=request.POST.get('tipo_impresora'),
            estado_id=request.POST.get('estado'),
            tecnico=request.user
        )
        return redirect('ver_equipos')

    context = {
        'direcciones': Direccion.objects.all(),
        'departamentos': Departamento.objects.all(),
        'tipos_impresora': TipoImpresora.objects.all(),
        'estados_impresora': EstadoImpresora.objects.all(),
    }
    return render(request, 'form_impresora.html', context)

@login_required
def exportar_impresoras_excel(request):
    filtro_tecnico = request.GET.get('tecnico', 'todos')
    query_busqueda = request.GET.get('q', '').strip()

    impresoras = ImpresoraRegistro.objects.select_related(
        'direccion', 'departamento', 'tipo_impresora', 'estado', 'tecnico'
    ).order_by('-fecha_creacion')

    if filtro_tecnico == 'mio':
        impresoras = impresoras.filter(tecnico=request.user)

    if query_busqueda:
        impresoras = impresoras.filter(
            departamento__nombre__icontains=query_busqueda
        ) | impresoras.filter(
            tipo_impresora__nombre__icontains=query_busqueda
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Impresoras Registradas"

    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='10174A', end_color='10174A', fill_type='solid')

    headers = ["Dirección", "Departamento", "Tipo de Impresora", "Estado", "Fecha Creación", "Técnico Registrador"]
    ws.append(headers)

    # Aplicar estilos a la primera fila (encabezados)
    for cell in ws[4]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for imp in impresoras:
        ws.append([
            imp.direccion.nombre if imp.direccion else "N/A",
            imp.departamento.nombre if imp.departamento else "N/A",
            imp.tipo_impresora.nombre if imp.tipo_impresora else "N/A",
            imp.estado.nombre if imp.estado else "N/A",
            imp.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            imp.tecnico.get_full_name() or imp.tecnico.username
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventario_impresoras_maipu.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_impresoras_csv(request):
    filtro_tecnico = request.GET.get('tecnico', 'todos')
    query_busqueda = request.GET.get('q', '').strip()

    impresoras = ImpresoraRegistro.objects.select_related(
        'direccion', 'departamento', 'tipo_impresora', 'estado', 'tecnico'
    ).order_by('-fecha_creacion')

    if filtro_tecnico == 'mio':
        impresoras = impresoras.filter(tecnico=request.user)

    if query_busqueda:
        impresoras = impresoras.filter(
            departamento__nombre__icontains=query_busqueda
        ) | impresoras.filter(
            tipo_impresora__nombre__icontains=query_busqueda
        )

    response = HttpResponse(content_type='text/text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="inventario_impresoras_maipu.csv"'
    writer = csv.writer(response, delimiter=';')

    writer.writerow(["Dirección", "Departamento", "Tipo de Impresora", "Estado", "Fecha Creación", "Técnico Registrador"])

    for imp in impresoras:
        writer.writerow([
            imp.direccion.nombre if imp.direccion else "N/A",
            imp.departamento.nombre if imp.departamento else "N/A",
            imp.tipo_impresora.nombre if imp.tipo_impresora else "N/A",
            imp.estado.nombre if imp.estado else "N/A",
            imp.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            imp.tecnico.get_full_name() or imp.tecnico.username
        ])

    return response