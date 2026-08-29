from database import query_db, execute_db


def user_has_reviewed(usuario_id, publicacion_id):
    result = query_db(
        "SELECT id FROM reseñas WHERE usuario_id = %s AND publicacion_id = %s",
        (usuario_id, publicacion_id), one=True
    )
    return result is not None


def create_review(usuario_id, publicacion_id, calificacion, comentario):
    return execute_db(
        "INSERT INTO reseñas (usuario_id, publicacion_id, calificacion, comentario) "
        "VALUES (%s, %s, %s, %s)",
        (usuario_id, publicacion_id, calificacion, comentario)
    )


def get_reviews_for_publication(publicacion_id):
    return query_db("""
        SELECT r.*, u.nombre
        FROM reseñas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.publicacion_id = %s
        ORDER BY r.fecha DESC
    """, (publicacion_id,))
    

def get_average_rating(publicacion_id):
    result = query_db(
        "SELECT AVG(calificacion) as promedio, COUNT(*) as total "
        "FROM reseñas WHERE publicacion_id = %s",
        (publicacion_id,), one=True
    )
    if not result or result['total'] == 0:
        return {'promedio': 0, 'total': 0}
    return {'promedio': round(float(result['promedio']), 1), 'total': result['total']}
