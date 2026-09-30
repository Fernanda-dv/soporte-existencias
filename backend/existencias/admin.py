from django.contrib import admin
from .models import Funcionario, Equipo, Monitor, ImpresoraRegistro


# ==========================================
# 1. INLINE DE MONITORES EN EQUIPO
# ==========================================

class MonitorInline(admin.TabularInline):
    model = Monitor
    extra = 0
    fields = ('pantalla_numero', 'marca', 'modelo', 'pulgadas', 'hdmi', 'numero_serie', 'numero_inventario')
    ordering = ('pantalla_numero',)


# ==========================================
# 2. ADMINISTRACIÓN DE FUNCIONARIOS
# ==========================================

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'departamento', 'anexo_display', 'cargo')
    list_filter = ('direccion', 'departamento', 'cargo')
    search_fields = ('nombre', 'anexo', 'direccion__nombre', 'departamento__nombre')

    @admin.display(description='Anexo', ordering='anexo')
    def anexo_display(self, obj):
        return obj.anexo or "N/A"


# ==========================================
# 3. ADMINISTRACIÓN DE EQUIPOS
# ==========================================

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    inlines = [MonitorInline]

    list_display = (
        'funcionario_nombre',
        'direccion',
        'departamento',
        'anexo',
        'cargo',
        'tipo',
        'marca',
        'modelo',
        'numero_serie_display',
        'numero_inventario_display',
        'ram',
        'disco',
        'procesador',
        'sistema_operativo',
        'tiene_monitor',
        'cantidad_monitores',
        'detalle_monitores',
        'tiene_impresora',
        'detalle_impresora',
        'fecha_creacion',
        'tecnico_nombre',
    )

    list_filter = (
        'tipo',
        'marca',
        'modelo',
        'ram',
        'disco',
        'procesador',
        'sistema_operativo',
        'tiene_monitor',
        'tiene_impresora',
        'fecha_creacion',
    )

    search_fields = (
        'funcionario__nombre',
        'numero_serie',
        'numero_inventario',
        'funcionario__direccion__nombre',
        'funcionario__departamento__nombre',
        'marca__nombre',
        'modelo__nombre',
        'tecnico__username',
        'tecnico__first_name',
        'tecnico__last_name',
    )

    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)

    # --- MÉTODOS PERSONALIZADOS PARA LIST_DISPLAY ---

    @admin.display(description='Funcionario', ordering='funcionario__nombre')
    def funcionario_nombre(self, obj):
        return obj.funcionario.nombre

    @admin.display(description='Dirección', ordering='funcionario__direccion__nombre')
    def direccion(self, obj):
        return obj.funcionario.direccion.nombre

    @admin.display(description='Departamento', ordering='funcionario__departamento__nombre')
    def departamento(self, obj):
        return obj.funcionario.departamento.nombre

    @admin.display(description='Anexo', ordering='funcionario__anexo')
    def anexo(self, obj):
        return obj.funcionario.anexo or "N/A"

    @admin.display(description='Cargo', ordering='funcionario__cargo__nombre')
    def cargo(self, obj):
        return obj.funcionario.cargo.nombre

    @admin.display(description='N° Serie', ordering='numero_serie')
    def numero_serie_display(self, obj):
        return obj.numero_serie or "N/A"

    @admin.display(description='N° Inventario', ordering='numero_inventario')
    def numero_inventario_display(self, obj):
        return obj.numero_inventario or "N/A"

    @admin.display(description='Cant. Monitores')
    def cantidad_monitores(self, obj):
        return obj.monitores.count() if obj.tiene_monitor else 0

    @admin.display(description='Detalle Monitores')
    def detalle_monitores(self, obj):
        if not obj.tiene_monitor:
            return "No"
        detalles = []
        for m in obj.monitores.all():
            marca = m.marca.nombre if m.marca else "S/M"
            modelo = m.modelo.nombre if m.modelo else "S/M"
            serie = m.numero_serie or "N/A"
            inv = m.numero_inventario or "N/A"
            detalles.append(f"P{m.pantalla_numero}: [{marca} {modelo}] Serie: {serie} / Inv: {inv}")
        return " | ".join(detalles)

    @admin.display(description='Detalle Impresora')
    def detalle_impresora(self, obj):
        if not obj.tiene_impresora:
            return "No"
        marca = obj.marca_impresora.nombre if obj.marca_impresora else "S/M"
        modelo = obj.modelo_impresora.nombre if obj.modelo_impresora else "S/M"
        serie = obj.numero_serie_impresora or "N/A"
        inv = obj.numero_inventario_impresora or "N/A"
        return f"[{marca} {modelo}] Serie: {serie} / Inv: {inv}"

    @admin.display(description='Técnico Registrador', ordering='tecnico__username')
    def tecnico_nombre(self, obj):
        return obj.tecnico.get_full_name() or obj.tecnico.username

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'funcionario', 'funcionario__direccion', 'funcionario__departamento',
            'funcionario__cargo', 'tipo', 'marca', 'modelo', 'ram', 'disco',
            'procesador', 'sistema_operativo', 'marca_impresora', 'modelo_impresora',
            'tecnico'
        ).prefetch_related('monitores', 'monitores__marca', 'monitores__modelo', 'monitores__pulgadas')


# ==========================================
# 4. ADMINISTRACIÓN DE IMPRESORAS
# ==========================================

@admin.register(ImpresoraRegistro)
class ImpresoraRegistroAdmin(admin.ModelAdmin):
    list_display = (
        'direccion',
        'departamento',
        'marca',
        'modelo',
        'numero_serie_display',
        'numero_inventario_display',
        'estado',
        'fecha_creacion',
        'tecnico_nombre',
    )

    list_filter = (
        'direccion',
        'departamento',
        'marca',
        'modelo',
        'estado',
        'fecha_creacion',
    )

    search_fields = (
        'direccion__nombre',
        'departamento__nombre',
        'marca__nombre',
        'modelo__nombre',
        'numero_serie',
        'numero_inventario',
        'estado__nombre',
        'tecnico__username',
        'tecnico__first_name',
        'tecnico__last_name',
    )

    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)

    @admin.display(description='N° Serie', ordering='numero_serie')
    def numero_serie_display(self, obj):
        return obj.numero_serie or "N/A"

    @admin.display(description='N° Inventario', ordering='numero_inventario')
    def numero_inventario_display(self, obj):
        return obj.numero_inventario or "N/A"

    @admin.display(description='Técnico Registrador', ordering='tecnico__username')
    def tecnico_nombre(self, obj):
        return obj.tecnico.get_full_name() or obj.tecnico.username

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'direccion', 'departamento', 'marca', 'modelo', 'estado', 'tecnico'
        )