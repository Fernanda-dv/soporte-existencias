from django.db import models
from django.core.validators import RegexValidator
from usuarios.models import Tecnico
from catalogos.models import (
    Direccion, Departamento, Cargo, TipoEquipo,
    MemoriaRAM, Disco, Procesador, SistemaOperativo,
    PulgadasMonitor, TipoImpresora, EstadoImpresora
)

class Funcionario(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    anexo = models.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d{4}$', 'El anexo debe ser un número de 4 dígitos.')]
    )
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.departamento})"

class Equipo(models.Model):
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='equipo')
    tipo = models.ForeignKey(TipoEquipo, on_delete=models.PROTECT)
    
    # Número de Serie e Inventario opcionales individualmente a nivel DB
    numero_serie = models.CharField(max_length=100, unique=True, null=True, blank=True)
    numero_inventario = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    ram = models.ForeignKey(MemoriaRAM, on_delete=models.PROTECT)
    disco = models.ForeignKey(Disco, on_delete=models.PROTECT)
    procesador = models.ForeignKey(Procesador, on_delete=models.PROTECT)
    sistema_operativo = models.ForeignKey(SistemaOperativo, on_delete=models.PROTECT)

    tiene_monitor = models.BooleanField()
    tiene_impresora = models.BooleanField()
    tipo_impresora = models.ForeignKey(TipoImpresora, on_delete=models.PROTECT, null=True, blank=True)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.PROTECT, related_name='equipos_registrados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registro_equipos'
        verbose_name = 'Registro de equipo'
        verbose_name_plural = 'Registros de equipos'

class Monitor(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='monitores')
    pantalla_numero = models.PositiveSmallIntegerField(default=1)
    pulgadas = models.ForeignKey(PulgadasMonitor, on_delete=models.PROTECT)
    hdmi = models.BooleanField(default=False)

class ImpresoraRegistro(models.Model):
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    tipo_impresora = models.ForeignKey(TipoImpresora, on_delete=models.PROTECT)
    estado = models.ForeignKey(EstadoImpresora, on_delete=models.PROTECT)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.PROTECT, related_name='impresoras_registradas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registro_impresoras'
        verbose_name = 'Registro de impresora'
        verbose_name_plural = 'Registros de impresoras'