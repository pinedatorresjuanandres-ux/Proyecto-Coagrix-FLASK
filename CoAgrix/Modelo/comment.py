from database import query_db, execute_db

MIN_LENGTH = 10
MAX_LENGTH = 300  # igual que la columna `comentarios.texto`
ESTADOS = ('Publicado', 'Oculto')


def clean_comment_text(raw):
    """Normaliza el texto de un comentario (junta espacios y saltos de línea:
    se muestra como una cita en un solo párrafo) y lo valida. Devuelve
    (texto, mensaje_de_error); el error es None si todo está bien."""
    texto = ' '.join((raw or '').split())
    if len(texto) < MIN_LENGTH:
        return texto, f'Escribe al menos {MIN_LENGTH} caracteres.'
    if len(texto) > MAX_LENGTH:
        return texto, f'El comentario no puede pasar de {MAX_LENGTH} caracteres.'
    return texto, None


def get_public_comments(limit=12):
    """Comentarios visibles en la página de inicio, del más reciente al más
    antiguo. Trae el rol y el municipio del autor (según el tipo de cuenta)
    para mostrar, por ejemplo, "Campesino, Marinilla"."""
    return query_db("""
        SELECT c.id, c.texto, u.nombre, r.nombre AS rol,
               COALESCE(ub_c.municipio, ub_e.municipio, ub_m.municipio) AS municipio
        FROM comentarios c
        JOIN usuarios u ON u.id = c.usuario_id
        JOIN roles r ON r.id = u.rol_id
        LEFT JOIN campesinos ca ON ca.usuario_id = u.id
        LEFT JOIN ubicaciones ub_c ON ub_c.id = ca.ubicacion_id
        LEFT JOIN empresas em ON em.usuario_id = u.id
        LEFT JOIN ubicaciones ub_e ON ub_e.id = em.ubicacion_id
        LEFT JOIN comerciantes co ON co.usuario_id = u.id
        LEFT JOIN ubicaciones ub_m ON ub_m.id = co.ubicacion_id
        WHERE c.estado = 'Publicado' AND u.estado = 'Activo'
        ORDER BY c.actualizado_en DESC, c.id DESC
        LIMIT %s
    """, (limit,)) or []


def get_user_comment(usuario_id):
    return query_db("SELECT id, texto, estado FROM comentarios WHERE usuario_id = %s", (usuario_id,), one=True)


def save_comment(usuario_id, texto):
    """Crea el comentario del usuario o, si ya tenía uno, lo reemplaza (un
    comentario por usuario). Al editar no se cambia `estado`: si un
    administrador lo ocultó, sigue oculto."""
    return execute_db(
        "INSERT INTO comentarios (usuario_id, texto) VALUES (%s, %s) "
        "ON DUPLICATE KEY UPDATE texto = VALUES(texto)",
        (usuario_id, texto)
    )


def delete_user_comment(usuario_id):
    return execute_db("DELETE FROM comentarios WHERE usuario_id = %s", (usuario_id,))


# ---- Administración ----

def list_comments_for_admin(filters=None, page=1, per_page=20):
    """Todos los comentarios (publicados y ocultos) con su autor, para el
    panel del administrador. Devuelve (comentarios, total)."""
    filters = filters or {}
    base = """
        FROM comentarios c
        JOIN usuarios u ON u.id = c.usuario_id
        JOIN roles r ON r.id = u.rol_id
        WHERE 1=1
    """
    params = []
    if filters.get('buscar'):
        base += " AND (u.nombre LIKE %s OR u.email LIKE %s OR c.texto LIKE %s)"
        like = f"%{filters['buscar']}%"
        params.extend([like, like, like])
    if filters.get('estado') in ESTADOS:
        base += " AND c.estado = %s"
        params.append(filters['estado'])

    total_row = query_db("SELECT COUNT(*) AS total " + base, tuple(params), one=True)
    total = total_row['total'] if total_row else 0

    page = max(1, page)
    rows = query_db(
        "SELECT c.id, c.texto, c.estado, c.creado_en, c.actualizado_en, "
        "u.nombre, u.email, r.nombre AS rol " + base +
        " ORDER BY c.actualizado_en DESC, c.id DESC LIMIT %s OFFSET %s",
        tuple(params) + (per_page, (page - 1) * per_page)
    ) or []
    return rows, total


def admin_update_comment(comentario_id, texto):
    return execute_db("UPDATE comentarios SET texto = %s WHERE id = %s", (texto, comentario_id))


def admin_set_comment_status(comentario_id, estado):
    if estado not in ESTADOS:
        return False
    return execute_db("UPDATE comentarios SET estado = %s WHERE id = %s", (estado, comentario_id))


def admin_delete_comment(comentario_id):
    return execute_db("DELETE FROM comentarios WHERE id = %s", (comentario_id,))
