from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import TecnicoLoginView, InicioView

urlpatterns = [
    path('', TecnicoLoginView.as_view(), name='login'),
    path('inicio/', InicioView.as_view(), name='inicio'),
    path('logout/', LogoutView.as_view(), name='logout'),
]