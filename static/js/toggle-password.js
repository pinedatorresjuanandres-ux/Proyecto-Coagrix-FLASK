// Alterna la visibilidad de un campo de contraseña.
// Uso: <span class="toggle-password" onclick="togglePassword('password', this)">👁️</span>
function togglePassword(inputId, iconEl) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        iconEl.textContent = '🙈';
    } else {
        input.type = 'password';
        iconEl.textContent = '👁️';
    }
}
