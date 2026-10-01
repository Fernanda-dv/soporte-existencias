document.addEventListener('DOMContentLoaded', function () {

    // ============================================================
    // 1. TRANSFORMAR NOMBRE DE FUNCIONARIO A MAYÚSCULAS
    // ============================================================
    const inputNombre = document.getElementById('funcionario_nombre');
    if (inputNombre) {
        inputNombre.addEventListener('input', function () {
            this.value = this.value.toUpperCase();
        });
    }


    // ============================================================
    // 2. FILTRADO DINÁMICO DE DEPARTAMENTO SEGÚN DIRECCIÓN
    // ============================================================
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

            // Limpiar si el departamento previo no corresponde a la nueva dirección
            if (!algunSeleccionado && !selectDepartamento.getAttribute('data-initial-loaded')) {
                selectDepartamento.value = '';
            }
            selectDepartamento.removeAttribute('data-initial-loaded');
        }

        if (selectDepartamento.value) {
            selectDepartamento.setAttribute('data-initial-loaded', 'true');
        }

        selectDireccion.addEventListener('change', filtrarDepartamentos);
        filtrarDepartamentos();
    }


    // ============================================================
    // 3. MÁSCARA Y MANTENIMIENTO DEL ANEXO
    // ============================================================
    const inputAnexo = document.getElementById('anexo');
    if (inputAnexo) {
        inputAnexo.addEventListener('input', function () {
            // Permitir solo dígitos numéricos
            this.value = this.value.replace(/\D/g, '');
        });
    }


    // ============================================================
    // 4. DESPLIEGUE PROGRESIVO DE SECCIÓN MONITOR
    // ============================================================
    const selectTieneMonitor = document.getElementById('tiene_monitor');
    const groupCantidadMonitor = document.getElementById('group-cantidad-monitor');
    const selectCantidadMonitores = document.getElementById('cantidad_monitores');
    const blockMonitor1 = document.getElementById('block-monitor-1');
    const blockMonitor2 = document.getElementById('block-monitor-2');

    function actualizarVisibilidadMonitores() {
        if (!selectTieneMonitor) return;

        const tieneMonitor = selectTieneMonitor.value;

        if (tieneMonitor === 'si') {
            if (groupCantidadMonitor) groupCantidadMonitor.classList.remove('is-hidden');

            const cantidad = selectCantidadMonitores ? selectCantidadMonitores.value : '';

            if (cantidad === '1') {
                if (blockMonitor1) blockMonitor1.classList.remove('is-hidden');
                if (blockMonitor2) blockMonitor2.classList.add('is-hidden');
            } else if (cantidad === '2') {
                if (blockMonitor1) blockMonitor1.classList.remove('is-hidden');
                if (blockMonitor2) blockMonitor2.classList.remove('is-hidden');
            } else {
                if (blockMonitor1) blockMonitor1.classList.add('is-hidden');
                if (blockMonitor2) blockMonitor2.classList.add('is-hidden');
            }
        } else {
            if (groupCantidadMonitor) groupCantidadMonitor.classList.add('is-hidden');
            if (blockMonitor1) blockMonitor1.classList.add('is-hidden');
            if (blockMonitor2) blockMonitor2.classList.add('is-hidden');

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
    actualizarVisibilidadMonitores();


    // ============================================================
    // 5. DESPLIEGUE PROGRESIVO DE SECCIÓN IMPRESORA
    // ============================================================
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
    actualizarVisibilidadImpresora();


    // ============================================================
    // 6. LECTOR DE CÓDIGO DE BARRAS / QR CON CÁMARA
    // ============================================================
    const barcodeModal = document.getElementById('barcode-modal');
    const btnCloseScanner = document.getElementById('btn-close-scanner');
    const btnCancelScanner = document.getElementById('btn-cancel-scanner');
    const scannerStatus = document.getElementById('scanner-status');
    const scannerLoading = document.getElementById('scanner-loading');
    const barcodeReader = document.getElementById('barcode-reader');

    let html5QrCode = null;
    let scannerRunning = false;
    let scannerStarting = false;
    let currentTargetInputId = 'numero_serie'; // Por defecto N° de Serie

    function setScannerStatus(message, type = 'normal') {
        if (!scannerStatus) return;

        let icon = 'fa-barcode';
        if (type === 'success') icon = 'fa-circle-check';
        else if (type === 'error') icon = 'fa-circle-exclamation';
        else if (type === 'loading') icon = 'fa-spinner fa-spin';

        scannerStatus.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;

        scannerStatus.classList.remove('scanner-success', 'scanner-error');
        if (type === 'success') scannerStatus.classList.add('scanner-success');
        if (type === 'error') scannerStatus.classList.add('scanner-error');
    }

    function openScannerModal(targetInputId) {
        if (!barcodeModal) return;
        currentTargetInputId = targetInputId || 'numero_serie';

        barcodeModal.classList.add('active');
        barcodeModal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('scanner-open');

        if (scannerLoading) scannerLoading.style.display = 'flex';
        setScannerStatus('Iniciando cámara...', 'loading');

        startBarcodeScanner();
    }

    async function closeScannerModal() {
        await stopBarcodeScanner();

        if (barcodeModal) {
            barcodeModal.classList.remove('active');
            barcodeModal.setAttribute('aria-hidden', 'true');
        }
        document.body.classList.remove('scanner-open');
    }

    async function startBarcodeScanner() {
        if (scannerRunning || scannerStarting) return;

        if (typeof Html5Qrcode === 'undefined') {
            setScannerStatus('No se pudo cargar la librería del lector.', 'error');
            if (scannerLoading) scannerLoading.style.display = 'none';
            return;
        }

        scannerStarting = true;

        try {
            html5QrCode = new Html5Qrcode('barcode-reader');

            const formatsToSupport = [
                Html5QrcodeSupportedFormats.CODE_128,
                Html5QrcodeSupportedFormats.CODE_39,
                Html5QrcodeSupportedFormats.CODE_93,
                Html5QrcodeSupportedFormats.EAN_13,
                Html5QrcodeSupportedFormats.EAN_8,
                Html5QrcodeSupportedFormats.UPC_A,
                Html5QrcodeSupportedFormats.UPC_E,
                Html5QrcodeSupportedFormats.ITF
            ];

            const config = {
                fps: 10,
                qrbox: function (vWidth, vHeight) {
                    const minEdge = Math.min(vWidth, vHeight);
                    return {
                        width: Math.floor(minEdge * 0.85),
                        height: Math.floor(minEdge * 0.35)
                    };
                },
                aspectRatio: 1.777778,
                formatsToSupport: formatsToSupport,
                disableFlip: false
            };

            const cameraConfig = { facingMode: { exact: "environment" } };

            try {
                await html5QrCode.start(cameraConfig, config, onBarcodeScanned, onBarcodeScanError);
            } catch (envError) {
                const cameras = await Html5Qrcode.getCameras();
                if (!cameras || cameras.length === 0) {
                    throw new Error('No se encontró ninguna cámara disponible.');
                }
                await html5QrCode.start(cameras.id, config, onBarcodeScanned, onBarcodeScanError);
            }

            scannerRunning = true;
            if (scannerLoading) scannerLoading.style.display = 'none';
            setScannerStatus('Apunte la cámara hacia el código de barras.', 'normal');

        } catch (error) {
            scannerRunning = false;
            if (scannerLoading) scannerLoading.style.display = 'none';
            setScannerStatus(error.message || 'No fue posible acceder a la cámara.', 'error');
        } finally {
            scannerStarting = false;
        }
    }

    async function onBarcodeScanned(decodedText) {
        if (!decodedText) return;

        const targetInput = document.getElementById(currentTargetInputId);
        if (targetInput) {
            targetInput.value = decodedText.trim();
            targetInput.dispatchEvent(new Event('input', { bubbles: true }));
            targetInput.dispatchEvent(new Event('change', { bubbles: true }));
        }

        setScannerStatus('Código detectado correctamente.', 'success');
        await stopBarcodeScanner();

        setTimeout(function () {
            if (barcodeModal) {
                barcodeModal.classList.remove('active');
                barcodeModal.setAttribute('aria-hidden', 'true');
            }
            document.body.classList.remove('scanner-open');
            if (targetInput) targetInput.focus();
        }, 500);
    }

    function onBarcodeScanError(errorMessage) {
        // Ignorar lecturas fallidas por cuadro
    }

    async function stopBarcodeScanner() {
        if (!html5QrCode) {
            scannerRunning = false;
            return;
        }
        try {
            if (scannerRunning) await html5QrCode.stop();
        } catch (e) {}
        try {
            html5QrCode.clear();
        } catch (e) {}

        html5QrCode = null;
        scannerRunning = false;
        scannerStarting = false;
        if (barcodeReader) barcodeReader.innerHTML = '';
    }

    // Vincular todos los botones de escaneo (.btn-scan-barcode)
    document.querySelectorAll('.btn-scan-barcode').forEach(btn => {
        btn.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target') || 'numero_serie';
            openScannerModal(targetId);
        });
    });

    if (btnCloseScanner) btnCloseScanner.addEventListener('click', closeScannerModal);
    if (btnCancelScanner) btnCancelScanner.addEventListener('click', closeScannerModal);

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && barcodeModal && barcodeModal.classList.contains('active')) {
            closeScannerModal();
        }
    });


    // ============================================================
    // 7. VALIDACIÓN PREVIA AL ENVÍO (ANEXO OPCIONAL)
    // ============================================================
    const form = document.getElementById('inventory-form');
    if (form) {
        form.addEventListener('submit', function (event) {
            const valAnexo = inputAnexo ? inputAnexo.value.trim() : '';

            // Se valida ÚNICAMENTE si el usuario ingresó algún valor
            if (valAnexo !== '' && valAnexo.length !== 4) {
                event.preventDefault();
                alert('Si ingresa un anexo, debe tener exactamente 4 dígitos.');
                inputAnexo.focus();
                return;
            }
        });
    }


    // ============================================================
    // 8. DETENER CÁMARA SI EL USUARIO ABANDONA LA PÁGINA
    // ============================================================
    window.addEventListener('beforeunload', function () {
        if (html5QrCode) {
            try {
                html5QrCode.stop();
            } catch (e) {}
        }
    });

});