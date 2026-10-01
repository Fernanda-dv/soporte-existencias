// Envía el formulario de filtro al cambiar el selector de técnico.
// (Reemplaza el antiguo onchange="..." en línea, que la política CSP del sitio no permite.)
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('select[data-autoenvio]').forEach(function (sel) {
        sel.addEventListener('change', function () {
            if (sel.form) { sel.form.submit(); }
        });
    });
});
