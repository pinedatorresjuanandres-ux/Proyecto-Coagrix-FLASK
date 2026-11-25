from database import query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash

def get_user_by_email(email):
    return query_db("SELECT * FROM usuarios WHERE email = %s", (email,), one=True)

def get_user_by_id(usuario_id):
    return query_db("SELECT * FROM usuarios WHERE id = %s", (usuario_id,), one=True)

def update_user_profile(usuario_id, nombre, email):
    return execute_db("UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s", (nombre, email, usuario_id))

def create_user(nombre, email, password, rol_id):
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO usuarios (nombre, email, password, rol_id, estado) VALUES (%s, %s, %s, %s, 'Activo')"
    return execute_db(query, (nombre, email, hashed_password, rol_id))

def update_user_password(usuario_id, new_password):
    """Guarda una nueva contraseña (siempre hasheada)."""
    return execute_db("UPDATE usuarios SET password = %s WHERE id = %s", (generate_password_hash(new_password), usuario_id))

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

def get_role_name(rol_id):
    role = query_db("SELECT nombre FROM roles WHERE id = %s", (rol_id,), one=True)
    return role['nombre'] if role else None

def get_farmer_data(usuario_id):
    return query_db("SELECT * FROM campesinos WHERE usuario_id = %s", (usuario_id,), one=True)

def get_company_data(usuario_id):
    return query_db("SELECT * FROM empresas WHERE usuario_id = %s", (usuario_id,), one=True)

def get_merchant_data(usuario_id):
    return query_db("SELECT * FROM comerciantes WHERE usuario_id = %s", (usuario_id,), one=True)

def get_buyers():
    """Usuarios con rol Comerciante o Empresa (compradores), para que un
    campesino los encuentre y pueda contactarlos desde Mensajes. Solo trae
    los datos necesarios para mostrarlos en esa lista (nunca la contraseña
    u otros datos sensibles)."""
    return query_db("""
        SELECT u.id, u.nombre, u.email, r.nombre as rol_nombre
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE r.nombre IN ('Comerciante', 'Empresa')
        ORDER BY u.nombre ASC
    """)

def create_location(departamento, municipio, direccion=None):
    return execute_db("INSERT INTO ubicaciones (departamento, municipio, direccion) VALUES (%s, %s, %s)", (departamento, municipio, direccion))

def update_location(ubicacion_id, departamento, municipio):
    return execute_db("UPDATE ubicaciones SET departamento = %s, municipio = %s WHERE id = %s", (departamento, municipio, ubicacion_id))

def create_farmer_profile(usuario_id, telefono=None, ubicacion_id=None, descripcion=None):
    """Crea la fila en 'campesinos' asociada al usuario recién registrado.
    Sin esto, el usuario existe en 'usuarios' pero no puede publicar
    productos (la FK campesino_id de 'publicaciones' quedaría inválida)."""
    query = "INSERT INTO campesinos (usuario_id, telefono, ubicacion_id, descripcion) VALUES (%s, %s, %s, %s)"
    return execute_db(query, (usuario_id, telefono, ubicacion_id, descripcion))

def create_company_profile(usuario_id, nit=None, telefono=None, ubicacion_id=None, sector=None):
    """Crea la fila en 'empresas' asociada al usuario recién registrado."""
    query = "INSERT INTO empresas (usuario_id, nit, telefono, ubicacion_id, sector) VALUES (%s, %s, %s, %s, %s)"
    return execute_db(query, (usuario_id, nit, telefono, ubicacion_id, sector))

def create_merchant_profile(usuario_id, telefono=None, ubicacion_id=None):
    """Crea la fila en 'comerciantes' asociada al usuario recién registrado."""
    query = "INSERT INTO comerciantes (usuario_id, telefono, ubicacion_id) VALUES (%s, %s, %s)"
    return execute_db(query, (usuario_id, telefono, ubicacion_id))

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
