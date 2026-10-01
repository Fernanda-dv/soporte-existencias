from django import forms

from catalogos.models import Cargo, Departamento, Direccion, Disco, Marca, MemoriaRAM, Procesador, PulgadasMonitor, SistemaOperativo, TipoEquipo, TipoImpresora
from .models import Funcionario, Equipo, Monitor

class EquipoIngresoForm(forms.Form):
    # --- FUNCIONARIO (Obligatorio) ---
    funcionario_nombre = forms.CharField(max_length=150, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=True)
    anexo = forms.CharField(max_length=4, required=False)
    cargo = forms.ModelChoiceField(queryset=Cargo.objects.all(), required=True)

    # --- EQUIPO (Obligatorio) ---
    tipo_equipo = forms.ModelChoiceField(queryset=TipoEquipo.objects.all(), required=True)
    numero_serie = forms.CharField(max_length=100, required=True)
    numero_inventario = forms.CharField(max_length=100, required=True)
    marca = forms.ModelChoiceField(queryset=Marca.objects.all(), required=True)
    ram = forms.ModelChoiceField(queryset=MemoriaRAM.objects.all(), required=True)
    disco = forms.ModelChoiceField(queryset=Disco.objects.all(), required=True)
    procesador = forms.ModelChoiceField(queryset=Procesador.objects.all(), required=True)
    sistema_operativo = forms.ModelChoiceField(queryset=SistemaOperativo.objects.all(), required=True)

    # --- MONITOR (Condicional) ---
    tiene_monitor = forms.TypedChoiceField(
        choices=[('si', 'Sí'), ('no', 'No')],
        coerce=lambda x: x == 'si',
        required=True
    )
    cantidad_monitores = forms.IntegerField(required=False, min_value=1, max_value=2)
    monitor1_pulgadas = forms.ModelChoiceField(queryset=PulgadasMonitor.objects.all(), required=False)
    monitor1_hdmi = forms.BooleanField(required=False)
    monitor2_pulgadas = forms.ModelChoiceField(queryset=PulgadasMonitor.objects.all(), required=False)
    monitor2_hdmi = forms.BooleanField(required=False)

    # --- IMPRESORA (Condicional) ---
    tiene_impresora = forms.TypedChoiceField(
        choices=[('si', 'Sí'), ('no', 'No')],
        coerce=lambda x: x == 'si',
        required=True
    )
    tipo_impresora = forms.ModelChoiceField(queryset=TipoImpresora.objects.all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar Monitor si la respuesta es SÍ
        if cleaned_data.get('tiene_monitor') is True:
            cant = cleaned_data.get('cantidad_monitores')
            if not cant:
                self.add_error('cantidad_monitores', 'Indique la cantidad de monitores.')
            
            if cant in [1, 2] and not cleaned_data.get('monitor1_pulgadas'):
                self.add_error('monitor1_pulgadas', 'Seleccione las pulgadas del Monitor 1.')
                
            if cant == 2 and not cleaned_data.get('monitor2_pulgadas'):
                self.add_error('monitor2_pulgadas', 'Seleccione las pulgadas del Monitor 2.')

        # Validar Impresora si la respuesta es SÍ
        if cleaned_data.get('tiene_impresora') is True:
            if not cleaned_data.get('tipo_impresora'):
                self.add_error('tipo_impresora', 'Seleccione el tipo de impresora.')

        return cleaned_data

    def clean_anexo(self):
        anexo = self.cleaned_data.get('anexo', '').strip()
        if anexo and len(anexo) != 4:
            raise forms.ValidationError('El anexo debe tener exactamente 4 dígitos.')
        return anexo or None