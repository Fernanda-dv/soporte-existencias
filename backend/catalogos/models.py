from django.db import models

class Direccion(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    def __str__(self): return self.nombre
    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

class Departamento(models.Model):
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='departamentos')
    nombre = models.CharField(max_length=150)
    def __str__(self): return f"{self.direccion.nombre} - {self.nombre}"
    class Meta:
        unique_together = ('direccion', 'nombre')

class Cargo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class TipoEquipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class MemoriaRAM(models.Model):
    tipo = models.CharField(max_length=50, unique=True, verbose_name="Tipo")
    def __str__(self): return self.tipo
    class Meta:
        verbose_name = "Memoria RAM"
        verbose_name_plural = "Memoria RAM"

class Disco(models.Model):
    tipo = models.CharField(max_length=100, unique=True, verbose_name="Tipo")
    def __str__(self): return self.tipo
    class Meta:
        verbose_name = "Disco"
        verbose_name_plural = "Discos"

class Procesador(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre
    class Meta:
        verbose_name = "Procesador"
        verbose_name_plural = "Procesadores"

class SistemaOperativo(models.Model):
    tipo = models.CharField(max_length=100, unique=True, verbose_name="Tipo")
    def __str__(self): return self.tipo
    class Meta:
        verbose_name = "Sistema Operativo"
        verbose_name_plural = "Sistemas Operativos"

class PulgadasMonitor(models.Model):
    tipo = models.CharField(max_length=50, unique=True, verbose_name="Tipo")
    def __str__(self): return self.tipo
    class Meta:
        verbose_name = "Pulgadas monitor"
        verbose_name_plural = "Pulgadas monitor"

class TipoImpresora(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class EstadoImpresora(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre
    class Meta:
        verbose_name = "Estado de Impresora"
        verbose_name_plural = "Estados de Impresoras"