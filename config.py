import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# En producción (FLASK_ENV=production) NO se permite arrancar con una
# SECRET_KEY por defecto: si falta la variable de entorno, se genera una
# aleatoria en cada arranque (lo cual invalida sesiones existentes) y se
# imprime una advertencia bien visible, en vez de usar un valor fijo y
# público como el que tenía este archivo originalmente.
_env = os.environ.get('FLASK_ENV', 'development').lower()
_secret_key = os.environ.get('SECRET_KEY')

if not _secret_key:
    if _env == 'production':
        print(
            "\n"
            "*** ADVERTENCIA DE SEGURIDAD ***\n"
            "No se definio la variable de entorno SECRET_KEY. Se genero una\n"
            "clave aleatoria SOLO para este arranque: todas las sesiones\n"
            "activas se invalidaran al reiniciar el servidor. Define\n"
            "SECRET_KEY en tu archivo .env antes de desplegar en produccion.\n"
        )
        _secret_key = secrets.token_hex(32)
    else:
        _secret_key = 'coagrix_dev_secret_key_do_not_use_in_production'


class Config:
    ENV = _env
    DEBUG = os.environ.get('FLASK_DEBUG', '1' if _env != 'production' else '0') == '1'
    SECRET_KEY = _secret_key

    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'coagrix'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)

    # Session Configuration
    SESSION_TYPE = 'filesystem'
    # OJO: el nombre de esta carpeta NO debe ser "flask_session" — si el
    # proyecto se ejecuta desde su propia carpeta raíz (que suele estar en
    # sys.path), una carpeta local llamada igual que el paquete instalado
    # "Flask-Session" tapa al paquete real y rompe
    # "from flask_session import Session" con un ImportError confuso.
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR') or os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '.flask_session_data'
    )
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Solo exige HTTPS para la cookie de sesion en produccion; en desarrollo
    # local (http://127.0.0.1) esto romperia el login si estuviera activo.
    SESSION_COOKIE_SECURE = _env == 'production'

    # Uploads Configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

    # CSRF (Flask-WTF)
    WTF_CSRF_TIME_LIMIT = None  # los tokens no expiran por tiempo dentro de la sesion

    # Rate limiting (Flask-Limiter)
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI') or 'memory://'
