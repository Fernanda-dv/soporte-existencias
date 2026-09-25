from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

class TecnicoLoginView(LoginView):
    template_name = "login.html"

class InicioView(
    LoginRequiredMixin,
    TemplateView
):
    template_name = "inicio.html"