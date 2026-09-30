document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // 1. AUTO-OCULTAR MENSAJES Y ALERTAS
    // ==========================================
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);
    }

    // ==========================================
    // 2. BÚSQUEDA EN TIEMPO REAL (LIVE SEARCH)
    // ==========================================
    // Aplica filtrado instantáneo en el navegador por cada tabla de forma independiente

    setupLiveSearch('q_eq');
    setupLiveSearch('q_imp');

    /**
     * Configura la búsqueda rápida en el cliente para un input específico.
     * @param {string} inputName - Atributo name del campo de texto (q_eq o q_imp)
     */
    function setupLiveSearch(inputName) {
        const searchInput = document.querySelector(`input[name="${inputName}"]`);
        if (!searchInput) return;

        const form = searchInput.closest('form');
        if (!form) return;

        const toolbarCard = form.closest('.toolbar-card');
        if (!toolbarCard) return;

        // Localizar el contenedor de la tabla inmediatamente siguiente a la barra de herramientas
        let tableContainer = toolbarCard.nextElementSibling;
        while (tableContainer && !tableContainer.classList.contains('table-responsive-container')) {
            tableContainer = tableContainer.nextElementSibling;
        }

        if (!tableContainer) return;

        const tableBody = tableContainer.querySelector('tbody');
        if (!tableBody) return;

        const rows = tableBody.querySelectorAll('tr:not(.empty-table-msg)');
        const emptyRow = tableBody.querySelector('.empty-table-msg');

        searchInput.addEventListener('input', function () {
            const query = this.value.toLowerCase().trim();
            let visibleCount = 0;

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            // Mostrar el mensaje de tabla vacía si el filtro en cliente oculta todas las filas
            if (emptyRow) {
                if (visibleCount === 0 && rows.length > 0) {
                    emptyRow.style.display = '';
                    const emptyText = emptyRow.querySelector('p');
                    if (emptyText) {
                        emptyText.textContent = `No se encontraron registros que coincidan con "${this.value}" en esta vista.`;
                    }
                } else if (visibleCount > 0) {
                    emptyRow.style.display = 'none';
                }
            }
        });
    }

    // ==========================================
    // 3. RESALTADO VISUAL DE FILAS AL HACER CLIC
    // ==========================================
    const dataTables = document.querySelectorAll('.data-table');
    dataTables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr:not(.empty-table-msg)');
        rows.forEach(row => {
            row.addEventListener('click', function (e) {
                // No activar si se hace clic en botones de edición o enlaces
                if (e.target.closest('a') || e.target.closest('button')) return;

                rows.forEach(r => r.classList.remove('selected-row'));
                this.classList.add('selected-row');
            });
        });
    });

});