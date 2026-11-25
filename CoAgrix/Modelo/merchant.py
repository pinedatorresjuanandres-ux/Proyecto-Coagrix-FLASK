from database import query_db, execute_db

def get_merchant_profile(usuario_id):
    return query_db("""SELECT m.*, u.nombre, u.email, ub.departamento, ub.municipio, ub.direccion
        FROM comerciantes m JOIN usuarios u ON u.id = m.usuario_id
        LEFT JOIN ubicaciones ub ON ub.id = m.ubicacion_id WHERE m.usuario_id = %s""", (usuario_id,), one=True)

def update_merchant_profile(usuario_id, telefono):
    return execute_db("UPDATE comerciantes SET telefono = %s WHERE usuario_id = %s", (telefono, usuario_id))
