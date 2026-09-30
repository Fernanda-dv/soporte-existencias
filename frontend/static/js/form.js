document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // 1. FILTRADO DINÁMICO DE DEPARTAMENTOS POR DIRECCIÓN
    // ==========================================
    const selectDireccion = document.getElementById('direccion');
    const selectDepartamento = document.getElementById('departamento');

    if (selectDireccion && selectDepartamento) {
        function filtrarDepartamentos() {
            const direccionId = selectDireccion.value;
            const opcionesDepto = selectDepartamento.querySelectorAll('option');

            if (!direccionId) {
                selectDepartamento.value = '';
                selectDepartamento.disabled = true;
                opcionesDepto.forEach(opt => {
                    if (opt.value !== '') opt.style.display = 'none';
                });
                return;
            }

            selectDepartamento.disabled = false;
            let algunSeleccionado = false;

            opcionesDepto.forEach(opt => {
                if (opt.value === '') {
                    opt.style.display = 'block';
                    return;
                }
                const deptoDir = opt.getAttribute('data-direccion');
                if (deptoDir === direccionId) {
                    opt.style.display = 'block';
                    if (opt.selected) algunSeleccionado = true;
                } else {
                    opt.style.display = 'none';
                }
            });

            // Si el departamento seleccionado previamente no corresponde a la nueva dirección, limpiar
            if (!algunSeleccionado && !selectDepartamento.getAttribute('data-initial-loaded')) {
                selectDepartamento.value = '';
            }
            selectDepartamento.removeAttribute('data-initial-loaded');
        }

        // Marcar carga inicial para modo edición
        if (selectDepartamento.value) {
            selectDepartamento.setAttribute('data-initial-loaded', 'true');
        }

        selectDireccion.addEventListener('change', filtrarDepartamentos);
        filtrarDepartamentos(); // Ejecutar al cargar
    }


    // ==========================================
    // 2. DESPLIEGUE PROGRESIVO DE SECCIÓN MONITOR
    // ==========================================
    const selectTieneMonitor = document.getElementById('tiene_monitor');
    const groupCantidadMonitor = document.getElementById('group-cantidad-monitor');
    const selectCantidadMonitores = document.getElementById('cantidad_monitores');
    const blockMonitor1 = document.getElementById('block-monitor-1');
    const blockMonitor2 = document.getElementById('block-monitor-2');

    function actualizarVisibilidadMonitores() {
        if (!selectTieneMonitor) return;

        const tieneMonitor = selectTieneMonitor.value;

        if (tieneMonitor === 'si') {
            // Mostrar la pregunta de cantidad
            if (groupCantidadMonitor) groupCantidadMonitor.classList.remove('is-hidden');

            // Evaluar cuántos monitores hay seleccionados
            const cantidad = selectCantidadMonitores ? selectCantidadMonitores.value : '';

            if (cantidad === '1') {
                if (blockMonitor1) blockMonitor1.classList.remove('is-hidden');
                if (blockMonitor2) blockMonitor2.classList.add('is-hidden');
            } else if (cantidad === '2') {
                if (blockMonitor1) blockMonitor1.classList.remove('is-hidden');
                if (blockMonitor2) blockMonitor2.classList.remove('is-hidden');
            } else {
                // Si aún no elige cantidad, mantener pantallas ocultas
                if (blockMonitor1) blockMonitor1.classList.add('is-hidden');
                if (blockMonitor2) blockMonitor2.classList.add('is-hidden');
            }
        } else {
            // Si selecciona "No" o está en blanco, ocultar todo el grupo
            if (groupCantidadMonitor) groupCantidadMonitor.classList.add('is-hidden');
            if (blockMonitor1) blockMonitor1.classList.add('is-hidden');
            if (blockMonitor2) blockMonitor2.classList.add('is-hidden');

            // Limpiar selección de cantidad si cambió a No
            if (tieneMonitor === 'no' && selectCantidadMonitores) {
                selectCantidadMonitores.value = '';
            }
        }
    }

    if (selectTieneMonitor) {
        selectTieneMonitor.addEventListener('change', actualizarVisibilidadMonitores);
    }
    if (selectCantidadMonitores) {
        selectCantidadMonitores.addEventListener('change', actualizarVisibilidadMonitores);
    }

    // Ejecutar al inicio para establecer estado (oculto en nuevo, visible si edita)
    actualizarVisibilidadMonitores();


    // ==========================================
    // 3. DESPLIEGUE PROGRESIVO DE SECCIÓN IMPRESORA
    // ==========================================
    const selectTieneImpresora = document.getElementById('tiene_impresora');
    const groupTipoImpresora = document.getElementById('group-tipo-impresora');

    function actualizarVisibilidadImpresora() {
        if (!selectTieneImpresora || !groupTipoImpresora) return;

        if (selectTieneImpresora.value === 'si') {
            groupTipoImpresora.classList.remove('is-hidden');
        } else {
            groupTipoImpresora.classList.add('is-hidden');
        }
    }

    if (selectTieneImpresora) {
        selectTieneImpresora.addEventListener('change', actualizarVisibilidadImpresora);
    }

    // Ejecutar al inicio para establecer estado
    actualizarVisibilidadImpresora();


    // ==========================================
    // 4. LÓGICA DEL LECTOR DE CÓDIGO DE BARRAS / QR (CÁMARA)
    // ==========================================
    const modalScanner = document.getElementById('barcode-modal');
    const btnCloseScanner = document.getElementById('btn-close-scanner');
    const btnCancelScanner = document.getElementById('btn-cancel-scanner');
    const scannerStatus = document.getElementById('scanner-status');
    const scannerLoading = document.getElementById('scanner-loading');

    let html5QrCode = null;
    let currentTargetInputId = null;

    // Vincular todos los botones con la clase .btn-scan-barcode
    document.querySelectorAll('.btn-scan-barcode').forEach(btn => {
        btn.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            if (targetId) {
                currentTargetInputId = targetId;
                abrirModalScanner();
            }
        });
    });

    function abrirModalScanner() {
        if (!modalScanner) return;
        modalScanner.style.display = 'flex';
        modalScanner.setAttribute('aria-hidden', 'false');
        iniciarCamara();
    }

    function cerrarModalScanner() {
        if (!modalScanner) return;
        detenerCamara().then(() => {
            modalScanner.style.display = 'none';
            modalScanner.setAttribute('aria-hidden', 'true');
        });
    }

    if (btnCloseScanner) btnCloseScanner.addEventListener('click', cerrarModalScanner);
    if (btnCancelScanner) btnCancelScanner.addEventListener('click', cerrarModalScanner);

    function iniciarCamara() {
        if (scannerLoading) scannerLoading.style.display = 'flex';
        if (scannerStatus) scannerStatus.innerHTML = '<i class="fa-solid fa-barcode"></i><span>Iniciando cámara...</span>';

        html5QrCode = new Html5Qrcode("barcode-reader");
        const config = { fps: 10, qrbox: { width: 250, height: 150 } };

        html5QrCode.start(
            { facingMode: "environment" },
            config,
            onScanSuccess
        ).then(() => {
            if (scannerLoading) scannerLoading.style.display = 'none';
            if (scannerStatus) scannerStatus.innerHTML = '<i class="fa-solid fa-camera"></i><span>Apunte al código de barras</span>';
        }).catch(err => {
            if (scannerLoading) scannerLoading.style.display = 'none';
            if (scannerStatus) scannerStatus.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i><span>Error al acceder a la cámara.</span>`;
        });
    }

    function onScanSuccess(decodedText) {
        if (currentTargetInputId) {
            const inputTarget = document.getElementById(currentTargetInputId);
            if (inputTarget) {
                inputTarget.value = decodedText.trim();
                // Destacar visualmente el campo actualizado
                inputTarget.style.borderColor = '#10174A';
                inputTarget.style.backgroundColor = '#eef2ff';
                setTimeout(() => {
                    inputTarget.style.borderColor = '';
                    inputTarget.style.backgroundColor = '';
                }, 1500);
            }
        }
        if (scannerStatus) {
            scannerStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i><span>Código detectado: ${decodedText}</span>`;
        }
        cerrarModalScanner();
    }

    function detenerCamara() {
        if (html5QrCode && html5QrCode.isScanning) {
            return html5QrCode.stop().then(() => {
                html5QrCode.clear();
            }).catch(() => {});
        }
        return Promise.resolve();
    }
});