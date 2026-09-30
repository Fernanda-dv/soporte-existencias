from django.test import TestCase, override_settings
from django.urls import reverse

from catalogos.models import (
    Cargo, Departamento, Direccion, Disco, MemoriaRAM, Procesador, SistemaOperativo, TipoEquipo,
)
from config.seguridad import celda_segura
from usuarios.models import Tecnico
from .models import Equipo, Funcionario


class CeldaSeguraTests(TestCase):
    def test_neutraliza_formulas(self):
        for v in ["=1+1", "+1", "-1", "@SUMA(A1)", "\t=x"]:
            self.assertTrue(celda_segura(v).startswith("'"))

    def test_no_toca_texto_normal(self):
        self.assertEqual(celda_segura("JUAN PÉREZ"), "JUAN PÉREZ")
        self.assertEqual(celda_segura(5), 5)


@override_settings(
    AXES_ENABLED=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class PermisosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        d = Direccion.objects.create(nombre="DITEC")
        dep = Departamento.objects.create(direccion=d, nombre="Soporte")
        func = Funcionario.objects.create(
            nombre="ANA", direccion=d, departamento=dep, anexo="1234",
            cargo=Cargo.objects.create(nombre="Analista"),
        )
        cls.tecnico = Tecnico.objects.create_user("tecnico", password="ClaveTecnico-2026!")
        cls.jefe = Tecnico.objects.create_user("jefe", password="ClaveJefe-2026!", is_staff=True)
        cls.equipo = Equipo.objects.create(
            funcionario=func, tipo=TipoEquipo.objects.create(nombre="Notebook"),
            numero_serie="SN1", ram=MemoriaRAM.objects.create(tipo="8 GB"),
            disco=Disco.objects.create(tipo="SSD"), procesador=Procesador.objects.create(nombre="i5"),
            sistema_operativo=SistemaOperativo.objects.create(tipo="Windows 11"),
            tiene_monitor=False, tiene_impresora=False, tecnico=cls.tecnico,
        )

    def test_tecnico_no_puede_editar(self):
        self.client.force_login(self.tecnico)
        r = self.client.get(reverse("editar_equipo", args=[self.equipo.pk]))
        self.assertEqual(r.status_code, 403)

    def test_admin_puede_editar(self):
        self.client.force_login(self.jefe)
        r = self.client.get(reverse("editar_equipo", args=[self.equipo.pk]))
        self.assertEqual(r.status_code, 200)

    def test_anonimo_va_al_login(self):
        r = self.client.get(reverse("ver_equipos"))
        self.assertEqual(r.status_code, 302)

    def test_datos_invalidos_no_producen_error_500(self):
        self.client.force_login(self.tecnico)
        r = self.client.post(reverse("ingresar_equipo"), {
            "funcionario_nombre": "X", "anexo": "12", "numero_serie": "N", "tiene_monitor": "si",
            "cantidad_monitores": "abc",
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "4 dígitos")
