
(function () {
    const REQUISITOS = [
        { texto: 'Mínimo 8 caracteres', test: (v) => v.length >= 8 },
        { texto: 'Al menos una letra mayúscula', test: (v) => /[A-Z]/.test(v) },
    ];

    document.addEventListener('DOMContentLoaded', function () {
        const password = document.getElementById('password');
        const confirm = document.getElementById('password_confirm');
        const boton = document.getElementById('btnRegistrarEmpresa');
        const checkbox = document.getElementById('aceptaTerminosEmpresa');
        if (!password || !boton) return;

        const lista = document.createElement('ul');
        lista.className = 'password-requisitos';
        REQUISITOS.forEach((req) => {
            const li = document.createElement('li');
            li.textContent = req.texto;
            lista.appendChild(li);
        });

        let matchItem = null;
        if (confirm) {
            matchItem = document.createElement('li');
            matchItem.textContent = 'Las contraseñas coinciden';
            lista.appendChild(matchItem);
        }

        const grupo = password.closest('.input-group') || password.parentElement;
        grupo.insertAdjacentElement('afterend', lista);

        function validar() {
            const valor = password.value;
            let valido = true;

            REQUISITOS.forEach((req, i) => {
                const ok = req.test(valor);
                lista.children[i].classList.toggle('cumplido', ok);
                if (!ok) valido = false;
            });

            if (confirm && matchItem) {
                const coincide = confirm.value.length > 0 && confirm.value === valor;
                matchItem.classList.toggle('cumplido', coincide);
                if (!coincide) valido = false;
            }

            const checkboxOk = !checkbox || checkbox.checked;
            boton.disabled = !(valido && checkboxOk);
        }

        password.addEventListener('input', validar);
        if (confirm) confirm.addEventListener('input', validar);
        if (checkbox) checkbox.addEventListener('change', validar);

        validar();
    });
})();
