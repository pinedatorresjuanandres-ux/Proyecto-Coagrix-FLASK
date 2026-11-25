import os
import secrets
from dotenv import load_dotenv

load_dotenv()

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

    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'coagrix2'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)

    SESSION_TYPE = 'filesystem'

    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR') or os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '.flask_session_data'
    )
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = _env == 'production'

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    WTF_CSRF_TIME_LIMIT = None  
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI') or 'memory://'
    # Límite de intentos (login, registro, comentarios). Apagado por defecto:
    # en Render y en redes compartidas (SENA) todos llegan con la misma IP y
    # se bloqueaban entre sí. Para activarlo: RATELIMIT_ENABLED=1
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', '0') == '1'

    # Correo saliente (recuperar contraseña). Si SMTP_HOST está vacío no se
    # envían correos: el enlace se imprime en la consola del servidor.
    SMTP_HOST = os.environ.get('SMTP_HOST') or ''
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USER = os.environ.get('SMTP_USER') or ''
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or ''
    SMTP_FROM = os.environ.get('SMTP_FROM') or os.environ.get('SMTP_USER') or 'no-reply@coagrix.local'
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', '0') == '1'  # 1 = puerto 465 (SSL); 0 = STARTTLS (587)
    # Envío por Google Apps Script (HTTPS). Si MAIL_SCRIPT_URL tiene valor,
    # se usa en lugar de SMTP. Ver docs/correo_google_apps_script.md
    MAIL_SCRIPT_URL = os.environ.get('MAIL_SCRIPT_URL') or ''
    MAIL_SCRIPT_SECRET = os.environ.get('MAIL_SCRIPT_SECRET') or ''
    # Dirección pública del sitio, para armar los enlaces de los correos
    # (ej. https://coagrix.com). Vacío = se usa la del navegador de quien pide.
    APP_BASE_URL = (os.environ.get('APP_BASE_URL') or '').rstrip('/')
