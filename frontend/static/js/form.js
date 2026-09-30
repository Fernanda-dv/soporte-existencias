document.addEventListener('DOMContentLoaded', function() {


    // ============================================================
    // 1. TRANSFORMAR NOMBRE DE FUNCIONARIO A MAYÚSCULAS
    // ============================================================

    const inputNombre = document.getElementById('funcionario_nombre');

    if (inputNombre) {

        inputNombre.addEventListener('input', function() {

            this.value = this.value.toUpperCase();

        });

    }



    // ============================================================
    // 2. FILTRO DINÁMICO DE DEPARTAMENTO SEGÚN DIRECCIÓN
    // ============================================================

    const selectDireccion = document.getElementById('direccion');
    const selectDepartamento = document.getElementById('departamento');

    if (selectDireccion && selectDepartamento) {

        const optionsDepartamento =
            Array.from(
                selectDepartamento.querySelectorAll(
                    'option[data-direccion]'
                )
            );


        selectDireccion.addEventListener('change', function() {

            const direccionId = this.value;


            // Restablecer selección
            selectDepartamento.value = '';


            if (direccionId) {

                selectDepartamento.disabled = false;


                optionsDepartamento.forEach(function(option) {

                    if (
                        option.getAttribute('data-direccion')
                        === direccionId
                    ) {

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



    // ============================================================
    // 3. VALIDACIÓN DE ANEXO
    // ============================================================

    const inputAnexo = document.getElementById('anexo');

    if (inputAnexo) {

        inputAnexo.addEventListener('input', function() {

            // Permitir solamente números
            this.value = this.value.replace(/\D/g, '');

        });

    }



    // ============================================================
    // 4. LÓGICA CONDICIONAL DE MONITORES
    // ============================================================

    const selectTieneMonitor =
        document.getElementById('tiene_monitor');

    const groupCantidadMonitor =
        document.getElementById('group-cantidad-monitor');

    const selectCantidadMonitores =
        document.getElementById('cantidad_monitores');


    const blockMonitor1 =
        document.getElementById('block-monitor-1');

    const blockMonitor2 =
        document.getElementById('block-monitor-2');


    const inputPulgadas1 =
        document.getElementById('monitor1_pulgadas');

    const inputPulgadas2 =
        document.getElementById('monitor2_pulgadas');


    const inputHdmi1 =
        document.getElementById('monitor1_hdmi');

    const inputHdmi2 =
        document.getElementById('monitor2_hdmi');



    function updateMonitorState() {

        if (!selectTieneMonitor) {
            return;
        }


        const tieneMonitor =
            selectTieneMonitor.value === 'si';


        if (tieneMonitor) {

            groupCantidadMonitor.style.display = 'block';

            selectCantidadMonitores.required = true;

            updateMonitorBlocks();

        } else {

            groupCantidadMonitor.style.display = 'none';

            selectCantidadMonitores.required = false;

            selectCantidadMonitores.value = '';


            blockMonitor1.style.display = 'none';

            blockMonitor2.style.display = 'none';


            inputPulgadas1.required = false;

            inputPulgadas1.value = '';

            inputHdmi1.checked = false;


            inputPulgadas2.required = false;

            inputPulgadas2.value = '';

            inputHdmi2.checked = false;

        }

    }



    function updateMonitorBlocks() {

        if (!selectCantidadMonitores) {
            return;
        }


        const cantidad =
            parseInt(selectCantidadMonitores.value) || 0;



        // Monitor 1

        if (cantidad >= 1) {

            blockMonitor1.style.display = 'block';

            inputPulgadas1.required = true;

        } else {

            blockMonitor1.style.display = 'none';

            inputPulgadas1.required = false;

            inputPulgadas1.value = '';

            inputHdmi1.checked = false;

        }



        // Monitor 2

        if (cantidad === 2) {

            blockMonitor2.style.display = 'block';

            inputPulgadas2.required = true;

        } else {

            blockMonitor2.style.display = 'none';

            inputPulgadas2.required = false;

            inputPulgadas2.value = '';

            inputHdmi2.checked = false;

        }

    }



    if (selectTieneMonitor) {

        selectTieneMonitor.addEventListener(
            'change',
            updateMonitorState
        );

    }


    if (selectCantidadMonitores) {

        selectCantidadMonitores.addEventListener(
            'change',
            updateMonitorBlocks
        );

    }



    // ============================================================
    // 5. LÓGICA CONDICIONAL DE IMPRESORA
    // ============================================================

    const selectTieneImpresora =
        document.getElementById('tiene_impresora');

    const groupTipoImpresora =
        document.getElementById('group-tipo-impresora');

    const selectTipoImpresora =
        document.getElementById('tipo_impresora');



    function updateImpresoraState() {

        if (!selectTieneImpresora) {
            return;
        }


        const tieneImpresora =
            selectTieneImpresora.value === 'si';


        if (tieneImpresora) {

            groupTipoImpresora.style.display = 'block';

            selectTipoImpresora.required = true;

        } else {

            groupTipoImpresora.style.display = 'none';

            selectTipoImpresora.required = false;

            selectTipoImpresora.value = '';

        }

    }



    if (selectTieneImpresora) {

        selectTieneImpresora.addEventListener(
            'change',
            updateImpresoraState
        );

    }



    // ============================================================
    // 6. LECTOR DE CÓDIGO DE BARRAS CON CÁMARA
    // ============================================================

    const numeroSerie =
        document.getElementById('numero_serie');

    const btnScanBarcode =
        document.getElementById('btn-scan-barcode');

    const barcodeModal =
        document.getElementById('barcode-modal');

    const btnCloseScanner =
        document.getElementById('btn-close-scanner');

    const btnCancelScanner =
        document.getElementById('btn-cancel-scanner');

    const scannerStatus =
        document.getElementById('scanner-status');

    const scannerLoading =
        document.getElementById('scanner-loading');

    const barcodeReader =
        document.getElementById('barcode-reader');



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


        // Se arma con nodos (no innerHTML) para que ningún texto se interprete como HTML.
        const iconEl = document.createElement('i');
        iconEl.className = `fa-solid ${icon}`;
        const textEl = document.createElement('span');
        textEl.textContent = message;
        scannerStatus.replaceChildren(iconEl, document.createTextNode(' '), textEl);


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

    const form =
        document.getElementById(
            'inventory-form'
        );


    if (form) {

        form.addEventListener(
            'submit',
            function(event) {

                if (
                    inputAnexo &&
                    inputAnexo.value.length !== 4
                ) {

                    event.preventDefault();


                    alert(
                        'El anexo debe tener exactamente 4 dígitos.'
                    );


                    inputAnexo.focus();

                    return;

                }

            }
        );

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