"""Utilidades de seguridad compartidas por el proyecto."""

import ipaddress

from django.conf import settings
from django.utils.csp import CSP


def ip_cliente(request):
    """IP real del usuario para django-axes.

    Detrás de HAProxy la conexión llega desde 127.0.0.1/Docker; HAProxy reemplaza siempre la
    cabecera X-Real-IP con la IP de origen, por lo que solo se confía en ella en ese caso.
    """
    if getattr(settings, "DETRAS_DE_PROXY", False):
        ip = request.META.get("HTTP_X_REAL_IP", "").strip()
        try:
            return str(ipaddress.ip_address(ip))
        except ValueError:
            pass
    return request.META.get("REMOTE_ADDR")


class CSPAdminMiddleware:
    """El panel /admin/ (Jazzmin) usa scripts y estilos en línea: se le permiten solo a esa ruta."""

    @staticmethod
    def _relajar(politica):
        if not politica:
            return politica
        return {
            **politica,
            "script-src": [CSP.SELF, CSP.UNSAFE_INLINE],
            "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],
        }

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin = self._relajar(getattr(settings, "SECURE_CSP", {}))
        self.admin_ro = self._relajar(getattr(settings, "SECURE_CSP_REPORT_ONLY", {}))

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/admin/"):
            response._csp_config = self.admin
            response._csp_ro_config = self.admin_ro
        return response


PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")


def celda_segura(valor):
    """Evita inyección de fórmulas al abrir exportaciones en Excel/LibreOffice (CSV injection)."""
    if isinstance(valor, str) and valor.startswith(PELIGROSOS):
        return "'" + valor
    return valor
