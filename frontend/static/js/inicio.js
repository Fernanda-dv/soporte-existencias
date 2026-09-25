document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Confirmación de Cierre de Sesión
    const logoutForm = document.querySelector('.logout-form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            const confirmLogout = confirm('¿Estás seguro de que deseas cerrar la sesión?');
            if (!confirmLogout) {
                e.preventDefault();
            }
        });
    }

    // 2. Feedback visual al tocar tarjetas en teléfonos táctiles
    const cards = document.querySelectorAll('.action-card');
    cards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        card.addEventListener('touchend', function() {
            this.style.transform = 'translateY(-6px)';
        });
    });
});