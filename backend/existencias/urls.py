from django.urls import path
from . import views

urlpatterns = [
    # Rutas de Equipos
    path('ingresar/', views.ingresar_equipo, name='ingresar_equipo'),
    path('equipos/', views.ver_equipos, name='ver_equipos'),
    path('equipos/editar/<int:equipo_id>/', views.editar_equipo, name='editar_equipo'),
    
    # Rutas de Exportación
    path('equipos/exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('equipos/exportar/csv/', views.exportar_csv, name='exportar_csv'),
    path('impresoras/exportar/excel/', views.exportar_impresoras_excel, name='exportar_impresoras_excel'),
    path('impresoras/exportar/csv/', views.exportar_impresoras_csv, name='exportar_impresoras_csv'),

    # Rutas de Impresoras
    path('impresoras/ingresar/', views.ingresar_impresora, name='ingresar_impresora'),
]