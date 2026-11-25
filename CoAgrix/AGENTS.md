# AGENTS.md — CoAgrix
Marketplace agrícola colombiano: los campesinos publican productos y los comerciantes y
empresas los compran. Cuatro roles: Administrador (1), Campesino (2), Empresa (3) y
Comerciante (4).

## Stack y estructura
- Python + Flask 3, MySQL (`mysql-connector-python`), Jinja2, Flask-WTF (CSRF),
  Flask-Limiter, Flask-Session (sesiones en archivos), Pillow.
- Patrón MVC con nombres en español:
  - `Modelo/` — acceso a datos y reglas. Todo el SQL vive aquí, usando `query_db` y
    `execute_db` de `database.py`.
  - `Controlador/` — un blueprint por área (`auth`, `farmer`, `admin`, `company`,
    `merchant`, `product`, `cart`, `message`, `appointment`, `account`, `comment`). Delgados:
    validan, llaman al modelo y renderizan.
  - `Vista/` — plantillas Jinja (`base.html`, `components/`, una carpeta por rol).
  - `static/` (css, js, uploads), `sql/` (esquema y migraciones), `scripts/` (seeds),
    `tests/`.
- `app.py` registra los blueprints. `config.py` lee todo de variables de entorno.

## Comandos (Windows, PowerShell)
- Instalar: `pip install -r requirements.txt`
- Arrancar: `python app.py` (http://localhost:5000)
- Tests: `pytest` (no necesitan MySQL: la capa de modelos se mockea)

## Convenciones
- Interfaz y mensajes `flash` en español. Código nuevo (funciones, variables) en inglés.
  Las tablas y columnas existentes en español se respetan tal cual.
- Precios con el filtro `|cop` (`$25.000 COP`). Teléfonos y NIT con las regex ya usadas en
  `auth_controller.py`.
- Cada pantalla nueva debe verse bien en móvil (375 px).
- Reutiliza antes de crear: mira `Modelo/` y `Vista/components/` primero.

## Seguridad (innegociable)
- Nunca leas, imprimas ni copies `.env`, `.flask_session_data/` ni `static/uploads/`.
  Para saber qué variables existen, usa `.env.example`.
- SQL siempre con parámetros `%s`. Prohibido concatenar datos del usuario.
- Todo `<form method="post">` lleva `csrf_token`. Las acciones que cambian estado son POST.
- Toda ruta protegida comprueba rol y, si toca datos ajenos, propiedad (ver `flask-security`).

## Forma de trabajar
- Haz solo lo que pide la spec activa. Cambios pequeños; no reescribas lo que funciona.
- Al terminar, resume qué cambiaste y qué decisiones debe revisar el usuario.

## Límites
- ✅ Siempre: tests en verde, textos en español, actualizar `MEMORY.md` al terminar.
- ⚠️ Pregunta antes: añadir dependencias, crear tablas o columnas, cambiar `sql/`,
  tocar `config.py`.
- 🚫 Nunca: borrar datos de usuarios, subir secretos al repositorio, desactivar CSRF o el
  rate limiting fuera de los tests.

## Verificación
- Lógica y rutas: `pytest`. No avanzar con tests en rojo.
- Interfaz: con el MCP de Chrome DevTools abre la app en local, prueba el flujo, revisa la
  consola y la vista móvil.

## Memoria
- Al empezar, lee `MEMORY.md`. Al terminar una tarea, actualízalo (máximo ~50 líneas).
- Si algo se vuelve regla permanente, propón moverlo aquí. Nunca guardes secretos.

## Reglas
- Lee `docs/constitution.md` y la spec activa (`specs/NNN-*/`) antes de tocar código.
