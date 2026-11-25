from database import query_db, execute_db


def get_company_profile(usuario_id):
    return query_db("""
        SELECT e.*, u.nombre, u.email, ub.departamento, ub.municipio, ub.direccion
        FROM empresas e
        JOIN usuarios u ON e.usuario_id = u.id
        LEFT JOIN ubicaciones ub ON e.ubicacion_id = ub.id
        WHERE e.usuario_id = %s
    """, (usuario_id,), one=True)


def update_company_profile(usuario_id, telefono, nit, sector):
    query = """
        UPDATE empresas
        SET telefono = %s, nit = %s, sector = %s
        WHERE usuario_id = %s
    """
    return execute_db(query, (telefono, nit, sector, usuario_id))
