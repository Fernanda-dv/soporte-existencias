document.addEventListener('DOMContentLoaded', function() {

    // Filtrado dinámico e instantáneo de Departamento según la Dirección seleccionada
    const selectDireccion = document.getElementById('direccion');
    const selectDepartamento = document.getElementById('departamento');
    
    if (selectDireccion && selectDepartamento) {
        const optionsDepartamento = Array.from(selectDepartamento.querySelectorAll('option[data-direccion]'));

        selectDireccion.addEventListener('change', function() {
            const direccionId = this.value;

            // Reiniciar selección
            selectDepartamento.value = '';

            if (direccionId) {
                selectDepartamento.disabled = false;
                
                // Mostrar solo los departamentos pertenecientes a la Dirección seleccionada
                optionsDepartamento.forEach(option => {
                    if (option.getAttribute('data-direccion') === direccionId) {
                        option.style.display = 'block';
                    } else {
                        option.style.display = 'none';
                    }
                });
            } else {
                selectDepartamento.disabled = true;
            }
        });
    }

});