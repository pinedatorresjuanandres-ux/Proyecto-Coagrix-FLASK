# 🌱 CoAgrix — Backend en Python (Flask)

Marketplace agrícola que conecta **campesinos** (venden productos del campo)
con **empresas** y **comerciantes** (compran al por mayor). Incluye además
un panel de **administrador** y una **API REST** para una futura app móvil
(React Native).

Construido con el patrón **MVC (Modelo–Vista–Controlador)**, Flask y MySQL.

---

## Índice

1. [Arquitectura y estructura de carpetas](#arquitectura-y-estructura-de-carpetas)
2. [Roles y flujo de la plataforma](#roles-y-flujo-de-la-plataforma)
3. [Requisitos](#requisitos)
4. [Instalación](#instalación)
5. [Usuarios de prueba](#usuarios-de-prueba)
6. [Componentes de interfaz (nuevo)](#componentes-de-interfaz-nuevo)
7. [Interactividad dinámica (nuevo)](#interactividad-dinámica-nuevo)
8. [API REST (para la app móvil)](#api-rest-para-la-app-móvil)
9. [Seguridad implementada](#seguridad-implementada)
10. [Pruebas](#pruebas)
11. [Qué le falta al proyecto](#qué-le-falta-al-proyecto)

---

## Arquitectura y estructura de carpetas

```
Proyecto-Coagrix-FLASK-main/
├── app.py                     # Punto de entrada: crea la app, registra blueprints,
│                               #   filtros de Jinja (|cop), manejadores de error
├── config.py                  # Configuración (lee variables de entorno con dotenv)
├── extensions.py              # Instancias compartidas (Flask-Limiter) para evitar
│                               #   imports circulares entre app.py y las rutas
├── database.py                # Conexión a MySQL + helpers query_db()/execute_db()
├── requirements.txt
├── .env.example                # Plantilla de variables de entorno
│
├── models/                    # Acceso a datos (una consulta SQL por función)
│   ├── user.py                 # Login, registro, hash de contraseñas, roles
│   ├── farmer.py                # Perfil y publicaciones del campesino
│   ├── company.py               # Perfil de empresa
│   ├── product.py               # Catálogo, categorías, publicaciones
│   ├── order.py                 # Pedidos y detalle de pedidos
│   ├── favorite.py               # Favoritos (usado por catálogo y API)
│   ├── review.py                 # Reseñas y calificación promedio
│   ├── message.py                # Mensajería entre usuarios
│   └── admin.py                  # Estadísticas y listados para el panel admin
│
├── controllers/                # Lógica de negocio: arma la respuesta con datos
│   │                            #   de models/ y decide qué template renderizar
│   ├── auth_controller.py        # Login/registro/recuperación de contraseña
│   ├── farmer_controller.py      # Panel, publicaciones y pedidos del campesino
│   ├── company_controller.py     # Panel y búsqueda de la empresa
│   ├── merchant_controller.py    # Panel y comparador de precios del comerciante
│   ├── product_controller.py     # Catálogo, detalle, favoritos, reseñas
│   ├── admin_controller.py       # Dashboard, usuarios y moderación de publicaciones
│   ├── favorite_controller.py    # Listado de "Mis favoritos"
│   ├── cart_controller.py        # Carrito y checkout (empresa/comerciante)
│   └── message_controller.py     # Bandeja de entrada y conversaciones
│
├── routes/                     # Blueprints de Flask: solo declaran URLs → controlador
│   ├── auth_routes.py, farmer_routes.py, company_routes.py, merchant_routes.py,
│   │   product_routes.py, admin_routes.py, cart_routes.py, message_routes.py
│   └── api_routes.py            # API REST con token Bearer (para la app móvil)
│
├── templates/                  # Vistas Jinja2
│   ├── base.html                 # Layout general: header, toasts, footer, modal, JS
│   ├── components/                # 🆕 Componentes reutilizables (ver sección aparte)
│   ├── farmer/ company/ merchant/ admin/   # Vistas específicas de cada panel
│   ├── errors/                    # 404 / 403 / 400 / 500 personalizados
│   └── *.html                     # index, catálogo, login, registro, detalle, etc.
│
├── static/
│   ├── css/ (theme.css, index.css, components.css 🆕, ...)
│   ├── js/ (components.js 🆕, toggle-password.js, terms-checkbox.js)
│   ├── img/
│   └── uploads/                  # Imágenes subidas por los campesinos
│
├── sql/
│   ├── coagrix.sql               # Esquema completo + datos de prueba
│   └── migracion_*.sql            # Migraciones sueltas (ver "Qué le falta")
│
└── tests/                       # Suite pytest (mockea la base de datos)
```

**Flujo de una petición típica:** `routes/*.py` recibe la URL → llama a una
función de `controllers/*.py` → el controlador pide datos a `models/*.py`
(que ejecuta SQL parametrizado vía `database.py`) → el controlador renderiza
un template de `templates/`, que a su vez puede incluir componentes de
`templates/components/`.

---

## Roles y flujo de la plataforma

| Rol | Qué puede hacer |
|---|---|
| **Campesino** | Publicar productos, ver y gestionar pedidos recibidos, mensajearse con compradores |
| **Empresa** | Buscar/filtrar catálogo, agregar al carrito, hacer pedidos, dejar reseñas, favoritos |
| **Comerciante** | Igual que Empresa, más un comparador de precios entre vendedores |
| **Administrador** | Ver estadísticas globales, gestionar usuarios (activar/desactivar/eliminar), moderar publicaciones |

---

## Requisitos

- Python 3.10+
- MySQL (por ejemplo vía XAMPP, o un servidor MySQL propio)
- Dependencias de Python — ver `requirements.txt`

## Instalación

1. **Base de datos**
   - Crea una base de datos `coagrix` en tu servidor MySQL.
   - Importa `sql/coagrix.sql` (por phpMyAdmin o `mysql -u root -p coagrix < sql/coagrix.sql`).

2. **Entorno de Python**
   ```bash
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Variables de entorno**
   - Copia `.env.example` a `.env` y ajusta las credenciales de MySQL.
   - Genera una `SECRET_KEY` real:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

4. **Ejecutar en desarrollo**
   ```bash
   python app.py
   ```
   Abre `http://127.0.0.1:5000`.

5. **Ejecutar en producción**
   No uses `python app.py` (servidor de desarrollo de Flask). Usa un
   servidor WSGI real, por ejemplo `waitress` (ya está en `requirements.txt`):
   ```bash
   FLASK_ENV=production waitress-serve --port=5000 app:app
   ```
   Define `FLASK_ENV=production` y una `SECRET_KEY` fija en el `.env` de producción.

## Usuarios de prueba

Solo existen si importaste `sql/coagrix.sql` de ejemplo. **Cámbialos antes
de usar datos reales.**

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | admin@coagrix.com | admin123 |
| Campesino | campesino@coagrix.com | campesino123 |
| Empresa | empresa@coagrix.com | empresa123 |
| Comerciante | comerciante@coagrix.com | comerciante123 |

---

## Componentes de interfaz (nuevo)

Antes, casi todo el HTML vivía repetido dentro de cada página (la tarjeta de
producto, el footer, la paginación, las alertas...). Se extrajo en
**macros e includes de Jinja** dentro de `templates/components/`, para que
cada pieza se edite en un solo lugar y se reutilice donde haga falta:

| Componente | Qué es | Dónde se usa hoy |
|---|---|---|
| `header.html` | Barra de navegación (ya existía) | `base.html` |
| `footer.html` | Pie de página | `base.html` |
| `flash_messages.html` | Puente entre `flash()` de Flask y los toasts de JS | `base.html` |
| `modal_confirm.html` | Modal de confirmación genérico (`data-confirm="..."`) | `base.html` |
| `product_card.html` | Macro `render_product_card(pub, ...)` — tarjeta de producto | `catalog.html`, `favorites.html` |
| `pagination.html` | Macro `render_pagination(...)` | `catalog.html` |
| `star_rating.html` | Macro `render_stars(promedio, total)` | `product_detail.html` |
| `empty_state.html` | Macro `render_empty_state(...)` para listas vacías | `catalog.html`, `favorites.html` |
| `stat_card.html` | Macro `render_stat_card(...)` con contador animado | `admin/dashboard.html`, `farmer/dashboard.html` |

**Cómo usar un componente nuevo en cualquier vista:**
```jinja
{% from 'components/product_card.html' import render_product_card %}
...
{{ render_product_card(pub, show_favorite=true, is_favorite=false) }}
```

**Dónde falta aplicarlos todavía** (quedan con HTML repetido, buenos
candidatos para la próxima limpieza): `templates/farmer/publications.html`,
`templates/company/search.html`, `templates/merchant/compare.html` y las
tablas de `templates/admin/*.html` podrían usar un futuro componente de
tabla/lista y de badge de estado.

## Interactividad dinámica (nuevo)

- **Favoritos sin recargar la página**: el corazón ♡/♥ del catálogo, de
  favoritos y del detalle de producto ahora hace `fetch()` a
  `/productos/<id>/favorito` en vez de enviar un formulario. El controlador
  (`toggle_favorite_action`) detecta la petición AJAX por el header
  `X-Requested-With: fetch` y responde JSON; si no hay JavaScript, el mismo
  endpoint sigue funcionando como antes (formulario + redirect), así que
  nada se rompe para usuarios sin JS.
- **Notificaciones "toast"**: los `flash()` de Flask ya no se muestran como
  cajas fijas arriba de la página — se convierten en notificaciones
  flotantes autodestruibles (`static/js/components.js` → `CxToast`).
- **Modal de confirmación**: cualquier `<form method="POST">` puede agregar
  `data-confirm="¿Seguro?"` y `data-confirm-title="..."` para mostrar un
  modal en vez del `confirm()` feo del navegador. Ya se aplicó a los 4
  formularios de "Eliminar" que existían (publicaciones y usuarios).
- **Contadores animados**: las tarjetas de estadísticas del panel admin y
  del campesino cuentan de 0 al número real al cargar la página
  (`data-cx-count` + `requestAnimationFrame`).

Todo esto vive en dos archivos nuevos, sin dependencias externas:
`static/css/components.css` y `static/js/components.js`.

## API REST (para la app móvil)

`routes/api_routes.py` expone una API bajo `/api/*` que usa un token
firmado (`Authorization: Bearer <token>`) en vez de cookies de sesión, para
que la futura app en React Native pueda consumirla sin depender del
navegador. Incluye autenticación, catálogo, favoritos, reseñas, carrito/checkout,
pedidos, mensajería y endpoints de administración. Está exenta de CSRF
(`csrf.exempt(api_bp)`) porque no usa formularios ni cookies de sesión.

## Seguridad implementada

- Contraseñas con hash (`werkzeug.security`); registros antiguos en texto
  plano se re-hashean automáticamente en el siguiente login exitoso.
- Protección CSRF (Flask-WTF) en todos los formularios POST de la web.
- Rate limiting (Flask-Limiter) en login y registro.
- Prevención de IDOR: un pedido solo lo ve/gestiona el comprador dueño o
  el campesino vendedor correspondiente.
- Validación real de imágenes subidas con Pillow (no solo la extensión) y
  límite de tamaño.
- Consultas SQL parametrizadas en toda la aplicación.
- Páginas de error personalizadas (404, 403, 400, 500).
- Cookies de sesión `HttpOnly`, `SameSite=Lax` y `Secure` en producción.

## Pruebas

```bash
pytest
```
Ver `tests/README.md` para el detalle de qué cubre la suite (no requiere
MySQL real: usa mocks sobre la capa de modelos).

---

## Qué le falta al proyecto

Esto es lo que encontré revisando el código a fondo — ordenado de más a
menos prioritario:

### Backend / datos
- **Migraciones versionadas**: hoy el esquema vive en `sql/coagrix.sql` más
  tres archivos `migracion_*.sql` sueltos que hay que aplicar a mano y en
  orden. Pasar a **Alembic** (o Flask-Migrate) evitaría que una base de
  datos existente quede desincronizada del código.
- **Sin pruebas contra MySQL real**: la suite de `pytest` mockea
  `query_db`/`execute_db`, así que un error de sintaxis SQL o un nombre de
  columna equivocado no lo detectan los tests, solo probarlo a mano.
- **Sin capa de logging estructurado** en producción más allá de
  `logging.basicConfig`; no hay trazabilidad de errores (por ejemplo,
  Sentry) ni métricas.
- **`favorite_controller.py` y el resto de listados no paginan**: `Mis
  favoritos`, `Mis publicaciones`, mensajes, etc. traen todos los registros
  de una sola vez. Si un usuario acumula muchos, la página se vuelve
  pesada. El catálogo y los listados de admin sí paginan (`test_pagination.py`)
  pero el patrón no se replicó en el resto.

### Frontend / UI
- **CSS inline en casi todas las vistas** (`style="..."` repetido por todos
  lados) en vez de clases reutilizables — dificulta mantener consistencia
  visual y hace las plantillas más largas de lo necesario. Ya se movieron
  algunas repeticiones a `components.css`, pero migrar el resto (dashboards
  de empresa/comerciante, `crear_publicacion.html`, `publicaciones.html`,
  las tablas de admin) es trabajo pendiente.
- **Favoritos y calificaciones no se muestran en todos los listados**: por
  ejemplo, `company/search.html` y `merchant/compare.html` no usan todavía
  `product_card.html` ni `star_rating.html` — quedaron con su propio
  marcado.
- **Sin componente de tabla/lista reutilizable** para las vistas de admin
  (usuarios, publicaciones) ni de badge de estado (Activo/Inactivo,
  Pendiente/Aprobada/Rechazada) — actualmente cada tabla define sus propios
  estilos de badge.
- **El carrito (`cart/`) no se probó ni se tocó** en esta ronda de cambios;
  sigue funcionando por recarga de página completa, sería un buen candidato
  para sumar interactividad (agregar/quitar cantidad sin recargar).
- **Accesibilidad**: faltan atributos ARIA en varios componentes
  interactivos (el menú de usuario del header, el dropdown), y el contraste
  de algunos textos grises sobre blanco (`color:#999`) es bajo.

### Producto / funcionalidad
- **No hay notificaciones en tiempo real** (websockets/polling) para
  mensajes nuevos o cambios de estado de pedido — hoy el usuario tiene que
  recargar para enterarse.
- **No hay subida de múltiples imágenes por publicación** en el flujo web
  (la tabla `archivos` y `product_detail.html` sí contemplan varias
  imágenes, pero el formulario de creación solo permite subir una).
- **El comparador de precios del comerciante** (`merchant/compare.html`) no
  se revisó a fondo en esta ronda; valdría la pena confirmar que agrupa
  bien por producto y no solo por publicación individual.
- **Panel de empresa/comerciante sin estadísticas** (a diferencia de admin y
  campesino, que sí muestran tarjetas de resumen) — sería sencillo
  agregarlas ahora que existe `stat_card.html`.

Ninguno de estos puntos es urgente para que el proyecto funcione, pero son
las brechas más claras entre "funciona" y "listo para producción con muchos
usuarios".
