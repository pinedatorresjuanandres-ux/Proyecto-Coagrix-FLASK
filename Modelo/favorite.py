from database import query_db, execute_db


def is_favorite(usuario_id, publicacion_id):
    result = query_db(
        "SELECT id FROM favoritos WHERE usuario_id = %s AND publicacion_id = %s",
        (usuario_id, publicacion_id), one=True
    )
    return result is not None


def add_favorite(usuario_id, publicacion_id):
    if is_favorite(usuario_id, publicacion_id):
        return True
    return execute_db(
        "INSERT INTO favoritos (usuario_id, publicacion_id) VALUES (%s, %s)",
        (usuario_id, publicacion_id)
    )


def remove_favorite(usuario_id, publicacion_id):
    return execute_db(
        "DELETE FROM favoritos WHERE usuario_id = %s AND publicacion_id = %s",
        (usuario_id, publicacion_id)
    )


def toggle_favorite(usuario_id, publicacion_id):
    """Agrega o quita de favoritos según el estado actual. Devuelve True si
    quedó marcado como favorito, False si quedó desmarcado."""
    if is_favorite(usuario_id, publicacion_id):
        remove_favorite(usuario_id, publicacion_id)
        return False
    add_favorite(usuario_id, publicacion_id)
    return True


def get_user_favorites(usuario_id):
    return query_db("""
        SELECT p.*, pr.nombre as producto_nombre, u.nombre as campesino_nombre
        FROM favoritos f
        JOIN publicaciones p ON f.publicacion_id = p.id
        JOIN productos pr ON p.producto_id = pr.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        WHERE f.usuario_id = %s
        ORDER BY f.id DESC
    """, (usuario_id,))
