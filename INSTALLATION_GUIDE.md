# Guía de Instalación - CoAgrix Backend

Esta guía proporciona instrucciones paso a paso para instalar y ejecutar el backend de CoAgrix en tu máquina local.

## Requisitos Previos

Asegúrate de tener instalados los siguientes programas:

- **XAMPP** (para MySQL y phpMyAdmin): Descárgalo desde [https://www.apachefriends.org/](https://www.apachefriends.org/)
- **Python 3.x**: Descárgalo desde [https://www.python.org/](https://www.python.org/)
- **Git** (opcional): Para clonar repositorios

## Paso 1: Configurar la Base de Datos

### 1.1 Iniciar XAMPP

Abre XAMPP y activa los módulos de **Apache** y **MySQL**. Haz clic en el botón "Start" junto a cada módulo.

### 1.2 Acceder a phpMyAdmin

Abre tu navegador web y ve a: `http://localhost/phpmyadmin/`

### 1.3 Crear la Base de Datos

En phpMyAdmin, sigue estos pasos:

1. Haz clic en la pestaña **"SQL"** en el menú superior.
2. Copia y pega el contenido del archivo `sql/coagrix.sql` en el editor SQL.
3. Haz clic en el botón **"Ejecutar"** para crear la base de datos y todas las tablas.

Alternativamente, puedes importar el archivo directamente:

1. Haz clic en **"Importar"** en el menú superior.
2. Selecciona el archivo `sql/coagrix.sql` desde tu computadora.
3. Haz clic en **"Ejecutar"**.

La base de datos `coagrix` ahora debe estar creada con todas las tablas y datos de prueba.

## Paso 2: Configurar el Entorno de Python

### 2.1 Navegar al Directorio del Proyecto

Abre una terminal (Command Prompt en Windows, Terminal en Mac/Linux) y navega al directorio del proyecto:

```bash
cd ruta/a/tu/proyecto/CoAgrix
```

### 2.2 Crear un Entorno Virtual (Recomendado)

Es recomendable crear un entorno virtual para aislar las dependencias del proyecto:

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Instalar Dependencias

Con el entorno virtual activado, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

### 2.4 Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

Abre el archivo `.env` y asegúrate de que las credenciales de MySQL sean correctas:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=coagrix
```

Si tu usuario de MySQL tiene una contraseña, agrégala en la línea `MYSQL_PASSWORD`.

## Paso 3: Ejecutar la Aplicación

### 3.1 Iniciar el Servidor Flask

Con el entorno virtual activado, ejecuta:

```bash
python app.py
```

Deberías ver un mensaje como:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 3.2 Acceder a la Aplicación

Abre tu navegador web y ve a: `http://127.0.0.1:5000`

Deberías ver la página de inicio de CoAgrix.

## Paso 4: Probar la Aplicación

### Usuarios de Prueba

Utiliza las siguientes credenciales para probar la aplicación:

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Administrador | admin@coagrix.com | admin123 |
| Campesino | campesino@coagrix.com | campesino123 |
| Empresa | empresa@coagrix.com | empresa123 |
| Comerciante | comerciante@coagrix.com | comerciante123 |

### Pruebas Recomendadas

1. **Iniciar Sesión**: Prueba con cada usuario de prueba.
2. **Panel del Campesino**: Crea publicaciones, consulta pedidos.
3. **Panel de Empresa**: Busca productos, realiza pedidos.
4. **Panel de Comerciante**: Compara precios entre vendedores.
5. **Panel Administrativo**: Consulta estadísticas del sistema.

## Solución de Problemas

### Error: "No module named 'mysql'"

Asegúrate de haber instalado las dependencias correctamente:

```bash
pip install -r requirements.txt
```

### Error: "Can't connect to MySQL server"

Verifica que:

1. XAMPP esté ejecutándose y MySQL esté activo.
2. Las credenciales en `.env` sean correctas.
3. La base de datos `coagrix` exista en phpMyAdmin.

### Error: "Template not found"

Asegúrate de que todos los archivos HTML estén en la carpeta `templates/` y que los nombres de los archivos sean correctos.

## Estructura del Proyecto

```
CoAgrix/
├── app.py                 # Punto de entrada
├── config.py              # Configuración
├── database.py            # Conexión a BD
├── requirements.txt       # Dependencias
├── .env.example           # Variables de entorno
├── models/                # Lógica de datos
├── controllers/           # Lógica de negocio
├── routes/                # Rutas de la aplicación
├── templates/             # Vistas HTML
├── static/                # CSS, JS, Imágenes
├── sql/
│   └── coagrix.sql        # Schema de BD
└── README.md              # Documentación
```

## Próximos Pasos

Una vez que la aplicación esté funcionando:

1. Personaliza los datos de prueba según tus necesidades.
2. Implementa funcionalidades adicionales según los requisitos.
3. Configura un servidor de producción (Gunicorn, Nginx).
4. Implementa medidas de seguridad adicionales.

## Soporte

Si encuentras problemas durante la instalación, verifica:

- Que Python esté correctamente instalado: `python --version`
- Que MySQL esté corriendo en XAMPP.
- Que todas las dependencias estén instaladas: `pip list`
- Que el archivo `.env` esté correctamente configurado.
