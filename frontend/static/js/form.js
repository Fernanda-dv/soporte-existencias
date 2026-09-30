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

    let scannerRunning = false;

    let scannerStarting = false;



    // ------------------------------------------------------------
    // Actualizar mensaje del lector
    // ------------------------------------------------------------

    function setScannerStatus(message, type = 'normal') {

        if (!scannerStatus) {
            return;
        }


        let icon = 'fa-barcode';


        if (type === 'success') {

            icon = 'fa-circle-check';

        } else if (type === 'error') {

            icon = 'fa-circle-exclamation';

        } else if (type === 'loading') {

            icon = 'fa-spinner fa-spin';

        }


        scannerStatus.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;


        scannerStatus.classList.remove(
            'scanner-success',
            'scanner-error'
        );


        if (type === 'success') {

            scannerStatus.classList.add(
                'scanner-success'
            );

        }


        if (type === 'error') {

            scannerStatus.classList.add(
                'scanner-error'
            );

        }

    }



    // ------------------------------------------------------------
    // Abrir modal
    // ------------------------------------------------------------

    function openScannerModal() {

        if (!barcodeModal) {
            return;
        }


        barcodeModal.classList.add('active');

        barcodeModal.setAttribute(
            'aria-hidden',
            'false'
        );


        document.body.classList.add(
            'scanner-open'
        );


        if (scannerLoading) {

            scannerLoading.style.display = 'flex';

        }


        setScannerStatus(
            'Iniciando cámara...',
            'loading'
        );


        startBarcodeScanner();

    }



    // ------------------------------------------------------------
    // Cerrar modal
    // ------------------------------------------------------------

    async function closeScannerModal() {

        await stopBarcodeScanner();


        if (barcodeModal) {

            barcodeModal.classList.remove(
                'active'
            );

            barcodeModal.setAttribute(
                'aria-hidden',
                'true'
            );

        }


        document.body.classList.remove(
            'scanner-open'
        );

    }



    // ------------------------------------------------------------
    // Iniciar lector
    // ------------------------------------------------------------

    async function startBarcodeScanner() {

        if (
            scannerRunning ||
            scannerStarting
        ) {
            return;
        }


        if (
            typeof Html5Qrcode === 'undefined'
        ) {

            setScannerStatus(
                'No se pudo cargar el lector de códigos.',
                'error'
            );

            if (scannerLoading) {
                scannerLoading.style.display = 'none';
            }

            return;
        }


        scannerStarting = true;


        try {

            html5QrCode =
                new Html5Qrcode(
                    'barcode-reader'
                );


            // Códigos de barras que se intentarán reconocer.
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

                qrbox: function(
                    viewfinderWidth,
                    viewfinderHeight
                ) {

                    const minEdge =
                        Math.min(
                            viewfinderWidth,
                            viewfinderHeight
                        );


                    return {

                        width: Math.floor(
                            minEdge * 0.85
                        ),

                        height: Math.floor(
                            minEdge * 0.35
                        )

                    };

                },

                aspectRatio: 1.777778,

                formatsToSupport:
                    formatsToSupport,

                disableFlip: false

            };



            // Preferimos cámara trasera en teléfonos/tablets.
            const cameraConfig = {
                facingMode: {
                    exact: 'environment'
                }
            };


            try {

                await html5QrCode.start(

                    cameraConfig,

                    config,

                    onBarcodeScanned,

                    onBarcodeScanError

                );

            } catch (environmentCameraError) {

                console.warn(
                    'No fue posible iniciar la cámara trasera:',
                    environmentCameraError
                );


                // Si no existe cámara trasera o no se puede
                // acceder a ella, utilizamos cualquier cámara.
                const cameras =
                    await Html5Qrcode.getCameras();


                if (
                    !cameras ||
                    cameras.length === 0
                ) {

                    throw new Error(
                        'No se encontró ninguna cámara disponible.'
                    );

                }


                await html5QrCode.start(

                    cameras[0].id,

                    config,

                    onBarcodeScanned,

                    onBarcodeScanError

                );

            }


            scannerRunning = true;


            if (scannerLoading) {

                scannerLoading.style.display = 'none';

            }


            setScannerStatus(
                'Apunte la cámara hacia el código de barras.',
                'normal'
            );


        } catch (error) {

            console.error(
                'Error iniciando lector:',
                error
            );


            scannerRunning = false;


            if (scannerLoading) {

                scannerLoading.style.display = 'none';

            }


            let message =
                'No fue posible acceder a la cámara.';


            if (
                error &&
                error.message
            ) {

                message =
                    error.message;

            }


            setScannerStatus(
                message,
                'error'
            );


        } finally {

            scannerStarting = false;

        }

    }



    // ------------------------------------------------------------
    // Código detectado
    // ------------------------------------------------------------

    async function onBarcodeScanned(
        decodedText,
        decodedResult
    ) {

        console.log(
            'Código detectado:',
            decodedText
        );


        if (!decodedText) {
            return;
        }


        // Escribir el código en el campo N° de Serie.
        if (numeroSerie) {

            numeroSerie.value =
                decodedText.trim();


            // Lanzar evento por si existe otra lógica
            // conectada al campo.
            numeroSerie.dispatchEvent(
                new Event(
                    'input',
                    {
                        bubbles: true
                    }
                )
            );

            numeroSerie.dispatchEvent(
                new Event(
                    'change',
                    {
                        bubbles: true
                    }
                )
            );

        }


        setScannerStatus(
            'Código detectado correctamente.',
            'success'
        );


        // Detener la cámara.
        await stopBarcodeScanner();


        // Cerrar el modal después de una pequeña pausa.
        setTimeout(function() {

            if (barcodeModal) {

                barcodeModal.classList.remove(
                    'active'
                );

                barcodeModal.setAttribute(
                    'aria-hidden',
                    'true'
                );

            }


            document.body.classList.remove(
                'scanner-open'
            );


            // Llevar el cursor al campo.
            if (numeroSerie) {

                numeroSerie.focus();

            }

        }, 500);

    }



    // ------------------------------------------------------------
    // Errores normales de lectura
    // ------------------------------------------------------------

    function onBarcodeScanError(errorMessage) {

        /*
         * Este evento se ejecuta constantemente mientras la cámara
         * está buscando un código.
         *
         * No mostramos errores al usuario porque es normal que
         * existan muchos frames donde todavía no se haya detectado
         * ningún código.
         */

    }



    // ------------------------------------------------------------
    // Detener cámara
    // ------------------------------------------------------------

    async function stopBarcodeScanner() {

        if (!html5QrCode) {

            scannerRunning = false;

            return;

        }


        try {

            if (scannerRunning) {

                await html5QrCode.stop();

            }

        } catch (error) {

            console.warn(
                'Error deteniendo cámara:',
                error
            );

        }


        try {

            html5QrCode.clear();

        } catch (error) {

            console.warn(
                'Error limpiando lector:',
                error
            );

        }


        html5QrCode = null;

        scannerRunning = false;

        scannerStarting = false;


        if (barcodeReader) {

            barcodeReader.innerHTML = '';

        }

    }



    // ------------------------------------------------------------
    // Eventos botones
    // ------------------------------------------------------------

    if (btnScanBarcode) {

        btnScanBarcode.addEventListener(
            'click',
            function() {

                openScannerModal();

            }
        );

    }


    if (btnCloseScanner) {

        btnCloseScanner.addEventListener(
            'click',
            function() {

                closeScannerModal();

            }
        );

    }


    if (btnCancelScanner) {

        btnCancelScanner.addEventListener(
            'click',
            function() {

                closeScannerModal();

            }
        );

    }



    // ------------------------------------------------------------
    // Cerrar con ESC
    // ------------------------------------------------------------

    document.addEventListener(
        'keydown',
        function(event) {

            if (
                event.key === 'Escape' &&
                barcodeModal &&
                barcodeModal.classList.contains(
                    'active'
                )
            ) {

                closeScannerModal();

            }

        }
    );



    // ============================================================
    // 7. VALIDACIÓN PREVIA AL ENVÍO
    // ============================================================

    const form = document.getElementById('inventory-form');

if (form) {
    form.addEventListener('submit', function(event) {
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

    window.addEventListener(
        'beforeunload',
        function() {

            if (html5QrCode) {

                try {

                    html5QrCode.stop();

                } catch (error) {

                    console.warn(error);

                }

            }

        }
    );

});