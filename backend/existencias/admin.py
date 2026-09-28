from django.contrib import admin
from .models import Equipo, ImpresoraRegistro


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
	list_display = (
		'funcionario_nombre', 'direccion', 'departamento', 'anexo', 'cargo',
		'tipo', 'numero_serie', 'numero_inventario', 'ram', 'disco',
		'procesador', 'sistema_operativo', 'tiene_monitor', 'cantidad_monitores',
		'detalle_monitores', 'tiene_impresora', 'tipo_impresora',
		'fecha_creacion', 'tecnico_nombre',
	)
	list_filter = ('tipo', 'tiene_monitor', 'tiene_impresora', 'fecha_creacion')
	search_fields = (
		'funcionario__nombre', 'numero_serie', 'numero_inventario',
		'funcionario__direccion__nombre', 'funcionario__departamento__nombre',
		'tecnico__username', 'tecnico__first_name', 'tecnico__last_name',
	)
	date_hierarchy = 'fecha_creacion'
	ordering = ('-fecha_creacion',)

	@admin.display(description='Funcionario', ordering='funcionario__nombre')
	def funcionario_nombre(self, obj):
		return obj.funcionario.nombre

	@admin.display(description='Dirección', ordering='funcionario__direccion__nombre')
	def direccion(self, obj):
		return obj.funcionario.direccion

	@admin.display(description='Departamento', ordering='funcionario__departamento__nombre')
	def departamento(self, obj):
		return obj.funcionario.departamento

	@admin.display(description='Anexo', ordering='funcionario__anexo')
	def anexo(self, obj):
		return obj.funcionario.anexo

	@admin.display(description='Cargo', ordering='funcionario__cargo__nombre')
	def cargo(self, obj):
		return obj.funcionario.cargo

	@admin.display(description='Cantidad de monitores')
	def cantidad_monitores(self, obj):
		return obj.monitores.count() if obj.tiene_monitor else 0

	@admin.display(description='Detalle de monitores')
	def detalle_monitores(self, obj):
		monitores = obj.monitores.all()
		detalle = ' / '.join(
			f"Pantalla {monitor.pantalla_numero}: {monitor.pulgadas.tipo} "
			f"(HDMI: {'Sí' if monitor.hdmi else 'No'})"
			for monitor in monitores
		)
		return detalle or 'N/A'

	@admin.display(description='Técnico registrador')
	def tecnico_nombre(self, obj):
		return obj.tecnico.get_full_name() or obj.tecnico.username

	def get_queryset(self, request):
		return super().get_queryset(request).select_related(
			'funcionario', 'funcionario__direccion', 'funcionario__departamento',
			'funcionario__cargo', 'tipo', 'ram', 'disco', 'procesador',
			'sistema_operativo', 'tipo_impresora', 'tecnico',
		).prefetch_related('monitores__pulgadas')


@admin.register(ImpresoraRegistro)
class ImpresoraRegistroAdmin(admin.ModelAdmin):
	list_display = (
		'direccion', 'departamento', 'tipo_impresora', 'estado',
		'fecha_creacion', 'tecnico_nombre',
	)
	list_filter = ('direccion', 'departamento', 'tipo_impresora', 'estado', 'fecha_creacion')
	search_fields = (
		'direccion__nombre', 'departamento__nombre', 'tipo_impresora__nombre',
		'estado__nombre', 'tecnico__username', 'tecnico__first_name',
		'tecnico__last_name',
	)
	date_hierarchy = 'fecha_creacion'
	ordering = ('-fecha_creacion',)

	@admin.display(description='Técnico registrador')
	def tecnico_nombre(self, obj):
		return obj.tecnico.get_full_name() or obj.tecnico.username

	def get_queryset(self, request):
		return super().get_queryset(request).select_related(
			'direccion', 'departamento', 'tipo_impresora', 'estado', 'tecnico',
		)
