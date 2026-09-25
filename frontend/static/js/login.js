document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Inyectar clases y placeholders a los inputs de Django si vienen limpios
    const usernameInput = document.querySelector('.input-wrapper input[name="username"]');
    const passwordInput = document.querySelector('.input-wrapper input[name="password"]');

    if (usernameInput) {
        usernameInput.setAttribute('placeholder', 'Nombre de Usuario');
        usernameInput.setAttribute('autocomplete', 'username');
        usernameInput.focus();
    }

    if (passwordInput) {
        passwordInput.setAttribute('placeholder', '••••••••');
        passwordInput.setAttribute('autocomplete', 'current-password');
    }

    // 2. Control de visibilidad de contraseña (Ojo Mostrar/Ocultar)
    const toggleBtn = document.getElementById('toggle-password');
    const toggleIcon = document.getElementById('toggle-password-icon');

    if (toggleBtn && passwordInput && toggleIcon) {
        toggleBtn.addEventListener('click', function() {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            
            // Alternar tipo de input
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            // Alternar icono FontAwesome
            toggleIcon.className = isPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
        });
    }

    // 3. Validación previa al envío
    const form = document.getElementById('inventory-login-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const userVal = usernameInput ? usernameInput.value.trim() : '';
            const passVal = passwordInput ? passwordInput.value.trim() : '';

            if (!userVal || !passVal) {
                e.preventDefault();
                alert('Por favor, completa los campos de usuario y contraseña antes de ingresar.');
            }
        });
    }

});
