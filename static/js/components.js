/* ============================================================
   CoAgrix — components.js
   Comportamiento compartido de los componentes reutilizables:
     - CxToast: notificaciones flotantes (reemplaza los <div class="alert">)
     - CxModal: modal de confirmación genérico basado en data-attributes
     - Favoritos por AJAX (sin recargar la página)
     - Contador animado para las tarjetas de estadísticas (cx-stat-value)
   No depende de ninguna librería externa.
   ============================================================ */
(function () {
  'use strict';

  /* ---------------- Toasts ---------------- */
  const CxToast = {
    container: null,
    icons: { success: '✅', error: '⚠️', info: 'ℹ️', warning: '⚠️' },

    ensureContainer() {
      if (!this.container) {
        this.container = document.getElementById('cxToastContainer');
      }
      return this.container;
    },

    show(message, category, timeout) {
      const container = this.ensureContainer();
      if (!container || !message) return;
      const type = ['success', 'error', 'info', 'warning'].includes(category) ? category : 'info';

      const toast = document.createElement('div');
      toast.className = `cx-toast cx-toast-${type}`;
      toast.setAttribute('role', 'status');
      toast.innerHTML = `
        <span class="cx-toast-icon">${this.icons[type]}</span>
        <span class="cx-toast-body"></span>
        <button type="button" class="cx-toast-close" aria-label="Cerrar">✕</button>
      `;
      toast.querySelector('.cx-toast-body').textContent = message;

      const remove = () => {
        toast.classList.add('cx-toast-leaving');
        setTimeout(() => toast.remove(), 200);
      };
      toast.querySelector('.cx-toast-close').addEventListener('click', remove);
      setTimeout(remove, timeout || 4500);

      container.appendChild(toast);
    }
  };
  window.CxToast = CxToast;

  /* ---------------- Modal de confirmación ---------------- */
  const CxModal = {
    overlay: null,
    pendingForm: null,

    init() {
      this.overlay = document.getElementById('cxConfirmModal');
      if (!this.overlay) return;
      this.overlay.querySelector('[data-cx-cancel]').addEventListener('click', () => this.close());
      this.overlay.addEventListener('click', (e) => { if (e.target === this.overlay) this.close(); });
      this.overlay.querySelector('[data-cx-confirm]').addEventListener('click', () => {
        const form = this.pendingForm;
        this.close();
        if (form) form.submit();
      });

      // Cualquier formulario o enlace con data-confirm="mensaje" pasa por aquí
      // en vez del confirm() nativo del navegador.
      document.addEventListener('submit', (e) => {
        const form = e.target;
        if (form instanceof HTMLFormElement && form.hasAttribute('data-confirm') && !form.dataset.cxConfirmed) {
          e.preventDefault();
          this.open(form, form.getAttribute('data-confirm'), form.getAttribute('data-confirm-title'));
        }
      });
    },

    open(form, message, title) {
      if (!this.overlay) return;
      this.pendingForm = form;
      this.overlay.querySelector('[data-cx-title]').textContent = title || '¿Estás seguro?';
      this.overlay.querySelector('[data-cx-message]').textContent = message || 'Esta acción no se puede deshacer.';
      this.overlay.classList.add('cx-modal-open');
    },

    close() {
      if (!this.overlay) return;
      this.overlay.classList.remove('cx-modal-open');
      this.pendingForm = null;
    }
  };
  window.CxModal = CxModal;

  /* ---------------- Favoritos dinámicos (AJAX) ---------------- */
  function initFavoriteButtons() {
    document.querySelectorAll('.cx-fav-btn[data-fav-url]').forEach((btn) => {
      if (btn.dataset.cxBound) return;
      btn.dataset.cxBound = '1';
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (btn.classList.contains('cx-fav-pending')) return;

        const url = btn.getAttribute('data-fav-url');
        const csrfToken = btn.getAttribute('data-csrf');
        btn.classList.add('cx-fav-pending');

        try {
          const response = await fetch(url, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'fetch',
              'X-CSRFToken': csrfToken
            }
          });
          if (!response.ok) throw new Error('request-failed');
          const data = await response.json();

          const active = !!data.favorito;
          btn.classList.toggle('cx-fav-active', active);
          btn.textContent = active ? '♥' : '♡';
          btn.title = active ? 'Quitar de favoritos' : 'Agregar a favoritos';
          btn.classList.remove('cx-fav-pending');
          btn.classList.add('cx-fav-pop');
          setTimeout(() => btn.classList.remove('cx-fav-pop'), 350);

          CxToast.show(active ? 'Agregado a favoritos.' : 'Quitado de favoritos.', 'success');
        } catch (err) {
          btn.classList.remove('cx-fav-pending');
          CxToast.show('No se pudo actualizar tus favoritos. Intenta de nuevo.', 'error');
        }
      });
    });
  }

  /* ---------------- Contador animado en tarjetas de estadísticas ---------------- */
  function animateCounters() {
    document.querySelectorAll('.cx-stat-value[data-cx-count]').forEach((el) => {
      const target = parseFloat(el.getAttribute('data-cx-count'));
      if (isNaN(target)) return;
      const prefix = el.getAttribute('data-cx-prefix') || '';
      const suffix = el.getAttribute('data-cx-suffix') || '';
      const duration = 700;
      const start = performance.now();

      function tick(now) {
        const progress = Math.min(1, (now - start) / duration);
        const value = Math.round(target * (1 - Math.pow(1 - progress, 3)));
        el.textContent = `${prefix}${value.toLocaleString('es-CO')}${suffix}`;
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }

  /* ---------------- Convierte los flash de Flask en toasts ---------------- */
  function flashesToToasts() {
    document.querySelectorAll('#cxFlashData [data-flash-message]').forEach((node) => {
      CxToast.show(node.getAttribute('data-flash-message'), node.getAttribute('data-flash-category'));
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    CxModal.init();
    initFavoriteButtons();
    animateCounters();
    flashesToToasts();
  });

  // Expuesto por si algún fragmento se inserta dinámicamente más adelante.
  window.CxComponents = { initFavoriteButtons, animateCounters };
})();
