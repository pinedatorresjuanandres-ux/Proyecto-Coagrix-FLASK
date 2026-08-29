from database import query_db, execute_db


def get_dashboard_stats():
    return {
        'total_usuarios': query_db("SELECT COUNT(*) as count FROM usuarios", one=True)['count'],
        'total_campesinos': query_db("SELECT COUNT(*) as count FROM campesinos", one=True)['count'],
        'total_empresas': query_db("SELECT COUNT(*) as count FROM empresas", one=True)['count'],
        'total_comerciantes': query_db("SELECT COUNT(*) as count FROM comerciantes", one=True)['count'],
        'total_productos': query_db("SELECT COUNT(*) as count FROM productos", one=True)['count'],
        'total_publicaciones': query_db("SELECT COUNT(*) as count FROM publicaciones", one=True)['count'],
        'total_pedidos': query_db("SELECT COUNT(*) as count FROM pedidos", one=True)['count'],
        'total_mensajes': query_db("SELECT COUNT(*) as count FROM mensajes", one=True)['count'],
    }


def get_recent_activity(limit=8):
    """Actividad reciente combinada: nuevos usuarios y nuevas publicaciones,
    ordenada por fecha para mostrar en el dashboard."""
    usuarios = query_db("""
        SELECT 'usuario' as tipo, nombre as titulo, fecha_registro as fecha
        FROM usuarios ORDER BY fecha_registro DESC LIMIT %s
    """, (limit,))
    publicaciones = query_db("""
        SELECT 'publicacion' as tipo, titulo, fecha_publicacion as fecha
        FROM publicaciones ORDER BY fecha_publicacion DESC LIMIT %s
    """, (limit,))
    actividad = (usuarios or []) + (publicaciones or [])
    actividad.sort(key=lambda x: x['fecha'], reverse=True)
    return actividad[:limit]


# ---------------------------------------------------------------------
# Gestión de usuarios
# ---------------------------------------------------------------------

def list_users(filters=None, page=None, per_page=20):
    filters = filters or {}
    base_query = """
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE 1=1
    """
    params = []

    if filters.get('buscar'):
        base_query += " AND (u.nombre LIKE %s OR u.email LIKE %s)"
        like = f"%{filters['buscar']}%"
        params.extend([like, like])

    if filters.get('rol'):
        base_query += " AND r.nombre = %s"
        params.append(filters['rol'])

    if filters.get('estado'):
        base_query += " AND u.estado = %s"
        params.append(filters['estado'])

    select_query = "SELECT u.*, r.nombre as rol_nombre " + base_query + " ORDER BY u.fecha_registro DESC"

    if page is None:
        return query_db(select_query, tuple(params))

    page = max(1, page)
    total_row = query_db("SELECT COUNT(*) as total " + base_query, tuple(params), one=True)
    total = total_row['total'] if total_row else 0

    select_query += " LIMIT %s OFFSET %s"
    items = query_db(select_query, tuple(params) + (per_page, (page - 1) * per_page))
    return items, total


def get_user_full_detail(usuario_id):
    return query_db("""
        SELECT u.*, r.nombre as rol_nombre
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.id = %s
    """, (usuario_id,), one=True)


def toggle_user_status(usuario_id):
    user = query_db("SELECT estado FROM usuarios WHERE id = %s", (usuario_id,), one=True)
    if not user:
        return None
    nuevo_estado = 'Inactivo' if user['estado'] == 'Activo' else 'Activo'
    execute_db("UPDATE usuarios SET estado = %s WHERE id = %s", (nuevo_estado, usuario_id))
    return nuevo_estado


def delete_user(usuario_id):
    return execute_db("DELETE FROM usuarios WHERE id = %s", (usuario_id,))


def get_all_roles():
    return query_db("SELECT * FROM roles")


# ---------------------------------------------------------------------
# Moderación de publicaciones
# ---------------------------------------------------------------------

def list_publications_for_moderation(filters=None, page=None, per_page=20):
    filters = filters or {}
    base_query = """
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        WHERE 1=1
    """
    params = []

    if filters.get('buscar'):
        base_query += " AND (p.titulo LIKE %s OR u.nombre LIKE %s)"
        like = f"%{filters['buscar']}%"
        params.extend([like, like])

    if filters.get('estado'):
        base_query += " AND p.estado = %s"
        params.append(filters['estado'])

    select_query = (
        "SELECT p.*, pr.nombre as producto_nombre, u.nombre as campesino_nombre " +
        base_query + " ORDER BY p.fecha_publicacion DESC"
    )

    if page is None:
        return query_db(select_query, tuple(params))

    page = max(1, page)
    total_row = query_db("SELECT COUNT(*) as total " + base_query, tuple(params), one=True)
    total = total_row['total'] if total_row else 0

    select_query += " LIMIT %s OFFSET %s"
    items = query_db(select_query, tuple(params) + (per_page, (page - 1) * per_page))
    return items, total


def set_publication_status(publicacion_id, estado):
    """estado: 'Activa' (aprobar) o 'Inactiva' (rechazar/ocultar)"""
    return execute_db("UPDATE publicaciones SET estado = %s WHERE id = %s", (estado, publicacion_id))
