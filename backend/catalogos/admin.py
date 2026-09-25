from django.contrib import admin
from .models import (
    Direccion, Departamento, Cargo, TipoEquipo, MemoriaRAM, Disco,
    Procesador, SistemaOperativo, PulgadasMonitor, TipoImpresora, EstadoImpresora
)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion')
    list_filter = ('direccion',)
    search_fields = ('nombre',)

@admin.register(MemoriaRAM)
class MemoriaRAMAdmin(admin.ModelAdmin):
    list_display = ('tipo',)

@admin.register(Disco)
class DiscoAdmin(admin.ModelAdmin):
    list_display = ('tipo',)

@admin.register(SistemaOperativo)
class SistemaOperativoAdmin(admin.ModelAdmin):
    list_display = ('tipo',)

@admin.register(PulgadasMonitor)
class PulgadasMonitorAdmin(admin.ModelAdmin):
    list_display = ('tipo',)

admin.site.register([
    Direccion, Cargo, TipoEquipo, Procesador, TipoImpresora, EstadoImpresora
])