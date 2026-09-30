from django.contrib import admin
from .models import (
    Direccion, Departamento, Cargo, TipoEquipo,
    MarcaEquipo, ModeloEquipo,
    MarcaMonitor, ModeloMonitor,
    MarcaImpresora, ModeloImpresora,
    MemoriaRAM, Disco, Procesador, SistemaOperativo, PulgadasMonitor, EstadoImpresora
)


# Registrar Marcas y Modelos Separados
@admin.register(MarcaEquipo)
class MarcaEquipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(ModeloEquipo)
class ModeloEquipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(MarcaMonitor)
class MarcaMonitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(ModeloMonitor)
class ModeloMonitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(MarcaImpresora)
class MarcaImpresoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(ModeloImpresora)
class ModeloImpresoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


# Resto de Catálogos
@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion')
    list_filter = ('direccion',)


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(TipoEquipo)
class TipoEquipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(MemoriaRAM)
class MemoriaRAMAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')


@admin.register(Disco)
class DiscoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')


@admin.register(Procesador)
class ProcesadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(SistemaOperativo)
class SistemaOperativoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')


@admin.register(PulgadasMonitor)
class PulgadasMonitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')


@admin.register(EstadoImpresora)
class EstadoImpresoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')