# Estructura del Proyecto CoAgrix

Este documento describe la arquitectura y organización del proyecto CoAgrix Backend.

## Arquitectura General

CoAgrix utiliza el patrón **MVC (Modelo-Vista-Controlador)** con Flask como framework web y MySQL como base de datos. La aplicación está organizada en módulos independientes para facilitar el mantenimiento y escalabilidad.

## Estructura de Directorios

```
CoAgrix/
├── app.py                          # Punto de entrada de la aplicación
├── config.py                       # Configuración centralizada
├── database.py                     # Gestión de conexiones a MySQL
├── requirements.txt                # Dependencias de Python
├── .env.example                    # Plantilla de variables de entorno
│
├── models/                         # Capa de Datos (Modelos)
│   ├── __init__.py
│   ├── user.py                     # Operaciones de usuarios
│   ├── farmer.py                   # Operaciones específicas de campesinos
│   ├── product.py                  # Gestión de productos y publicaciones
│   ├── order.py                    # Gestión de pedidos
│   └── message.py                  # Sistema de mensajería
│
├── controllers/                    # Capa de Lógica de Negocio
│   ├── __init__.py
│   ├── auth_controller.py          # Autenticación y autorización
│   ├── farmer_controller.py        # Lógica del panel del campesino
│   ├── admin_controller.py         # Lógica del panel administrativo
│   ├── company_controller.py       # Lógica del panel empresarial
│   ├── merchant_controller.py      # Lógica del panel del comerciante
│   └── product_controller.py       # Lógica del catálogo de productos
│
├── routes/                         # Rutas y Blueprints
│   ├── __init__.py
│   ├── auth_routes.py              # Rutas de autenticación
│   ├── farmer_routes.py            # Rutas del panel del campesino
│   ├── admin_routes.py             # Rutas del panel administrativo
│   ├── company_routes.py           # Rutas del panel empresarial
│   ├── merchant_routes.py          # Rutas del panel del comerciante
│   └── product_routes.py           # Rutas del catálogo
│
├── templates/                      # Vistas (Jinja2 Templates)
│   ├── base.html                   # Plantilla base con header y footer
│   ├── index.html                  # Página de inicio
│   ├── login.html                  # Selector de rol para login
│   ├── login_agricultor.html       # Login del campesino
│   ├── login_empresa.html          # Login de la empresa
│   ├── login_comerciante.html      # Login del comerciante
│   ├── registro.html               # Registro de usuarios
│   ├── catalog.html                # Catálogo de productos
│   ├── product_detail.html         # Detalle de un producto
│   ├── crear_publicacion.html      # Crear nueva publicación
│   │
│   ├── farmer/                     # Vistas del campesino
│   │   ├── dashboard.html          # Panel principal
│   │   ├── profile.html            # Perfil del campesino
│   │   └── publications.html       # Mis publicaciones
│   │
│   ├── company/                    # Vistas de la empresa
│   │   ├── dashboard.html          # Panel principal
│   │   └── search.html             # Búsqueda de productos
│   │
│   ├── merchant/                   # Vistas del comerciante
│   │   ├── dashboard.html          # Panel principal
│   │   └── compare.html            # Comparación de precios
│   │
│   └── admin/                      # Vistas del administrador
│       └── dashboard.html          # Panel de administración
│
├── static/                         # Archivos estáticos
│   ├── css/                        # Hojas de estilos
│   │   ├── index.css
│   │   ├── login.css
│   │   ├── login_agricultor.css
│   │   ├── login_empresa.css
│   │   ├── login_comerciante.css
│   │   ├── registro.css
│   │   ├── header.css
│   │   ├── crear_publiccaion.css
│   │   └── mis_publicaciones.css
│   ├── js/                         # Scripts JavaScript
│   ├── img/                        # Imágenes
│   │   └── logo.png
│   └── uploads/                    # Archivos subidos por usuarios
│
├── sql/                            # Scripts de base de datos
│   └── coagrix.sql                 # Schema completo con datos de prueba
│
├── README.md                       # Documentación principal
├── INSTALLATION_GUIDE.md           # Guía de instalación
└── PROJECT_STRUCTURE.md            # Este archivo
```

## Descripción de Componentes

### 1. Capa de Datos (models/)

**user.py**: Gestiona operaciones relacionadas con usuarios, incluyendo búsqueda, creación y recuperación de información de roles específicos.

**farmer.py**: Contiene operaciones específicas para campesinos como gestión de cultivos, publicaciones, pedidos recibidos y estadísticas de ventas.

**product.py**: Maneja productos, categorías y publicaciones activas con capacidad de filtrado por categoría y ubicación.

**order.py**: Gestiona la creación, actualización y consulta de pedidos y sus detalles.

**message.py**: Implementa el sistema de mensajería entre usuarios con funcionalidad de conversaciones.

### 2. Capa de Lógica de Negocio (controllers/)

**auth_controller.py**: Implementa el flujo de autenticación con validación de credenciales, estado del usuario y redirección según rol.

**farmer_controller.py**: Maneja la creación de publicaciones y gestión de contenido del campesino.

**admin_controller.py**: Proporciona estadísticas del sistema y datos para el dashboard administrativo.

**company_controller.py**: Gestiona la búsqueda de productos y pedidos para empresas.

**merchant_controller.py**: Implementa comparación de precios y gestión de pedidos para comerciantes.

**product_controller.py**: Maneja el catálogo de productos con filtros y detalles de productos.

### 3. Rutas (routes/)

Cada blueprint define las rutas específicas para su módulo y aplica protecciones de acceso según el rol del usuario. Todas las rutas están prefijadas con su módulo correspondiente (ej: `/farmer/`, `/company/`).

### 4. Vistas (templates/)

Utilizan **Jinja2** como motor de plantillas. La plantilla `base.html` proporciona estructura común con header y footer. Las vistas específicas de cada rol heredan de `base.html` y personalizan el contenido.

## Flujo de Autenticación

1. Usuario accede a `/login` y selecciona su rol.
2. Completa el formulario de login con email y contraseña.
3. `auth_controller.py` valida las credenciales contra la base de datos.
4. Si son válidas, se crea una sesión con los datos del usuario.
5. El usuario es redirigido a su panel correspondiente según su rol.

## Flujo de Datos

```
Usuario → Ruta (routes/) → Controlador (controllers/) → Modelo (models/) → BD (MySQL)
                                                                    ↓
                                          Respuesta JSON/HTML ← Plantilla (templates/)
```

## Base de Datos

La base de datos `coagrix` contiene las siguientes tablas principales:

- **usuarios**: Almacena información de usuarios con roles
- **roles**: Define los 4 roles del sistema (Administrador, Campesino, Empresa, Comerciante)
- **campesinos**: Información específica de campesinos
- **empresas**: Información específica de empresas
- **comerciantes**: Información específica de comerciantes
- **productos**: Catálogo de productos
- **categorias**: Categorías de productos
- **cultivos**: Cultivos registrados por campesinos
- **publicaciones**: Productos publicados para venta
- **pedidos**: Órdenes de compra
- **detalle_pedidos**: Detalles de cada pedido
- **mensajes**: Sistema de mensajería
- **notificaciones**: Notificaciones del sistema
- **favoritos**: Productos guardados por usuarios
- **reseñas**: Calificaciones de productos
- **ubicaciones**: Información geográfica
- **historial**: Registro de acciones
- **archivos**: Imágenes y archivos asociados

## Seguridad

- **Consultas Parametrizadas**: Todas las consultas SQL utilizan parámetros para prevenir inyección SQL.
- **Sesiones**: Gestión de sesiones con Flask-Session.
- **Validación de Roles**: Protección de rutas según el rol del usuario.
- **Manejo de Errores**: Validación del lado del servidor para todas las entradas.

## Convenciones de Código

- **Nombres de Archivos**: snake_case (ej: `auth_controller.py`)
- **Nombres de Funciones**: snake_case (ej: `get_user_by_email()`)
- **Nombres de Clases**: PascalCase (aunque no se usan muchas clases)
- **Nombres de Variables**: snake_case
- **Comentarios**: En español para coherencia con el proyecto

## Extensibilidad

El proyecto está diseñado para ser fácilmente extensible:

1. **Nuevos Roles**: Agregar un nuevo rol requiere crear un nuevo blueprint en `routes/`, un controlador en `controllers/`, y vistas en `templates/`.
2. **Nuevas Funcionalidades**: Seguir el patrón MVC: crear modelo, controlador, rutas y vistas.
3. **Nuevas Tablas**: Agregar al `coagrix.sql` y crear modelos correspondientes.

## Próximas Mejoras Sugeridas

1. Implementar autenticación con tokens JWT.
2. Agregar validación de email con confirmación.
3. Implementar recuperación de contraseña.
4. Agregar pruebas unitarias.
5. Implementar logging centralizado.
6. Agregar paginación en listados.
7. Implementar búsqueda full-text.
8. Agregar notificaciones en tiempo real con WebSockets.
