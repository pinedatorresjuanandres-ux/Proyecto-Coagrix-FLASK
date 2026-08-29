from database import query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash

def get_user_by_email(email):
    return query_db("SELECT * FROM usuarios WHERE email = %s", (email,), one=True)

def get_user_by_id(usuario_id):
    return query_db("SELECT * FROM usuarios WHERE id = %s", (usuario_id,), one=True)

def create_user(nombre, email, password, rol_id):
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO usuarios (nombre, email, password, rol_id, estado) VALUES (%s, %s, %s, %s, 'Activo')"
    return execute_db(query, (nombre, email, hashed_password, rol_id))

def verify_password(stored_password, plain_password):
    """Verifica la contraseña contra el hash guardado.
    Soporta también cuentas antiguas que quedaron con contraseña en texto
    plano (creadas antes de este cambio), para no romper su acceso."""
    try:
        if check_password_hash(stored_password, plain_password):
            return True
    except ValueError:
        pass
    return stored_password == plain_password

def upgrade_password_if_plaintext(user_id, stored_password, plain_password):
    """Si el login fue exitoso por coincidencia en texto plano (cuenta
    antigua), aprovecha para re-hashear la contraseña en ese momento.
    Así las cuentas viejas quedan seguras solas, sin script manual."""
    if stored_password == plain_password:
        new_hash = generate_password_hash(plain_password)
        execute_db("UPDATE usuarios SET password = %s WHERE id = %s", (new_hash, user_id))

def set_reset_token(user_id, token, expira):
    """Guarda el token de recuperación de contraseña y su expiración."""
    query = "UPDATE usuarios SET reset_token = %s, reset_token_expira = %s WHERE id = %s"
    return execute_db(query, (token, expira, user_id))

def get_user_by_reset_token(token):
    """Devuelve el usuario dueño de este token, solo si aún no expiró."""
    return query_db(
        "SELECT * FROM usuarios WHERE reset_token = %s AND reset_token_expira > NOW()",
        (token,), one=True
    )

def clear_reset_token(user_id):
    """Invalida el token de recuperación (se usa tras restablecer la
    contraseña, para que el mismo enlace no se pueda reutilizar)."""
    execute_db(
        "UPDATE usuarios SET reset_token = NULL, reset_token_expira = NULL WHERE id = %s",
        (user_id,)
    )

def update_password(user_id, new_password):
    """Actualiza la contraseña (siempre hasheada) y limpia el token de
    recuperación asociado."""
    hashed_password = generate_password_hash(new_password)
    execute_db("UPDATE usuarios SET password = %s WHERE id = %s", (hashed_password, user_id))
    clear_reset_token(user_id)

def get_role_name(rol_id):
    role = query_db("SELECT nombre FROM roles WHERE id = %s", (rol_id,), one=True)
    return role['nombre'] if role else None

def get_farmer_data(usuario_id):
    return query_db("SELECT * FROM campesinos WHERE usuario_id = %s", (usuario_id,), one=True)

def get_company_data(usuario_id):
    return query_db("SELECT * FROM empresas WHERE usuario_id = %s", (usuario_id,), one=True)

def get_merchant_data(usuario_id):
    return query_db("SELECT * FROM comerciantes WHERE usuario_id = %s", (usuario_id,), one=True)

def create_farmer_profile(usuario_id):
    """Crea la fila en 'campesinos' asociada al usuario recién registrado.
    Sin esto, el usuario existe en 'usuarios' pero no puede publicar
    productos (la FK campesino_id de 'publicaciones' quedaría inválida)."""
    query = "INSERT INTO campesinos (usuario_id) VALUES (%s)"
    return execute_db(query, (usuario_id,))

def create_company_profile(usuario_id):
    """Crea la fila en 'empresas' asociada al usuario recién registrado."""
    query = "INSERT INTO empresas (usuario_id) VALUES (%s)"
    return execute_db(query, (usuario_id,))

def create_merchant_profile(usuario_id):
    """Crea la fila en 'comerciantes' asociada al usuario recién registrado."""
    query = "INSERT INTO comerciantes (usuario_id) VALUES (%s)"
    return execute_db(query, (usuario_id,))

def get_or_create_farmer_profile(usuario_id):
    """Igual que get_farmer_data, pero si la cuenta es antigua y no tiene
    fila en 'campesinos' (por haberse registrado antes de la corrección),
    la crea automáticamente en este momento. Así no se necesita ejecutar
    SQL manual para reparar cuentas viejas."""
    farmer = get_farmer_data(usuario_id)
    if not farmer:
        create_farmer_profile(usuario_id)
        farmer = get_farmer_data(usuario_id)
    return farmer
