---
name: jinja-ui
description: Úsala siempre que crees o modifiques plantillas Jinja (Vista/), CSS o JavaScript de CoAgrix, o formularios y pantallas nuevas.
---
# Plantillas y UI en CoAgrix
## Estructura
- Las plantillas extienden `base.html`. Hay una carpeta por rol (`farmer/`, `admin/`,
  `cart/`, `messages/`...) y piezas reutilizables en `components/`
  (`header.html`, `badges.html`, `location_select.html`, `price_compare.html`).
- Reutiliza los componentes antes de crear HTML repetido.
- Los estilos van en `static/css/`; el JS, en `static/js/`. Usa `url_for('static', ...)`.
## Reglas
- Todo formulario POST lleva `csrf_token`.
- Precios: `{{ valor|cop }}`. Imágenes de producto: `{{ product_image_url(p.imagen) }}`.
- Jinja escapa por defecto: nunca uses `|safe` con texto que venga del usuario.
- Textos en español. Mensajes al usuario con `flash(..., 'error' | 'success')`.
- Accesibilidad: `<label>` asociado a cada campo, foco visible, contraste suficiente,
  `aria-live` en mensajes que cambian sin recargar.
- Responsive: comprueba 375 px. Para el diseño visual, apóyate en la skill `frontend-design`,
  respetando la identidad actual (`theme.css`, `coagrix-redesign.css`).
## Verificación
Abre la pantalla con el MCP de Chrome DevTools, prueba el flujo, revisa la consola y la vista móvil.
