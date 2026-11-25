import hashlib
import secrets

from mysql.connector import Error
from werkzeug.security import generate_password_hash

from database import query_db, execute_db, get_db_connection

TOKEN_MINUTES = 30
# Mínimo de minutos entre dos solicitudes para el mismo usuario (anti-spam
# de correos).
COOLDOWN_MINUTES = 2


def _hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def recent_reset_exists(usuario_id):
    """True si a este usuario ya se le generó un enlace hace muy poco."""
    row = query_db(
        "SELECT 1 FROM password_resets WHERE usuario_id = %s "
        "AND creado_en > DATE_SUB(NOW(), INTERVAL %s MINUTE) LIMIT 1",
        (usuario_id, COOLDOWN_MINUTES), one=True
    )
    return row is not None


def create_reset_token(usuario_id):
    """Genera un token aleatorio para el usuario, guarda solo su hash con
    vencimiento y devuelve el token en claro (para ponerlo en el correo).
    Devuelve None si no se pudo guardar."""
    token = secrets.token_urlsafe(32)
    saved = execute_db(
        "INSERT INTO password_resets (usuario_id, token_hash, expira_en) "
        "VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL %s MINUTE))",
        (usuario_id, _hash_token(token), TOKEN_MINUTES)
    )
    return token if saved else None


def is_reset_token_valid(token):
    """True si el token existe, no ha vencido y no se ha usado."""
    row = query_db(
        "SELECT 1 FROM password_resets WHERE token_hash = %s "
        "AND usado_en IS NULL AND expira_en > NOW() LIMIT 1",
        (_hash_token(token),), one=True
    )
    return row is not None


def consume_reset_token(token, new_password):
    """Cambia la contraseña del dueño del token y lo deja inutilizable, todo
    en una sola transacción. El bloqueo de la fila (FOR UPDATE) evita que el
    mismo enlace se use dos veces en paralelo. Además invalida cualquier otro
    enlace pendiente de ese usuario. Devuelve el `rol_id` del usuario si se
    cambió la contraseña (para llevarlo al login de su rol) o None si el
    token no es válido."""
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT pr.usuario_id, u.rol_id FROM password_resets pr "
            "JOIN usuarios u ON u.id = pr.usuario_id WHERE pr.token_hash = %s "
            "AND pr.usado_en IS NULL AND pr.expira_en > NOW() FOR UPDATE",
            (_hash_token(token),)
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return None
        cursor.execute(
            "UPDATE usuarios SET password = %s WHERE id = %s",
            (generate_password_hash(new_password), row['usuario_id'])
        )
        cursor.execute(
            "UPDATE password_resets SET usado_en = NOW() "
            "WHERE usuario_id = %s AND usado_en IS NULL",
            (row['usuario_id'],)
        )
        conn.commit()
        return row['rol_id']
    except Error as e:
        print(f"Reset password error: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()
