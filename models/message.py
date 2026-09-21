from database import query_db, execute_db

def send_message(remitente_id, destinatario_id, contenido):
    query = "INSERT INTO mensajes (remitente_id, destinatario_id, contenido) VALUES (%s, %s, %s)"
    return execute_db(query, (remitente_id, destinatario_id, contenido))

def get_messages_with_user(usuario_id, otro_usuario_id):
    return query_db("""
        SELECT * FROM mensajes 
        WHERE (remitente_id = %s AND destinatario_id = %s) 
           OR (remitente_id = %s AND destinatario_id = %s)
        ORDER BY fecha ASC
    """, (usuario_id, otro_usuario_id, otro_usuario_id, usuario_id))

def get_message_conversations(usuario_id):
    return query_db("""
        SELECT DISTINCT 
            CASE WHEN remitente_id = %s THEN destinatario_id ELSE remitente_id END as otro_usuario_id,
            u.nombre, u.email
        FROM mensajes m
        JOIN usuarios u ON u.id = CASE WHEN remitente_id = %s THEN destinatario_id ELSE remitente_id END
        WHERE remitente_id = %s OR destinatario_id = %s
        ORDER BY m.fecha DESC
    """, (usuario_id, usuario_id, usuario_id, usuario_id))

def mark_message_as_read(mensaje_id):
    query = "UPDATE mensajes SET leido = true WHERE id = %s"
    return execute_db(query, (mensaje_id,))

def mark_conversation_as_read(otro_usuario_id, usuario_id):
    """Marca como leídos todos los mensajes que 'otro_usuario_id' le envió
    a 'usuario_id' (se llama al abrir la conversación)."""
    query = "UPDATE mensajes SET leido = true WHERE remitente_id = %s AND destinatario_id = %s"
    return execute_db(query, (otro_usuario_id, usuario_id))

def get_unread_count(usuario_id):
    """Total de mensajes sin leer que ha recibido el usuario (para mostrar
    un contador/insignia en el header)."""
    result = query_db(
        "SELECT COUNT(*) as count FROM mensajes WHERE destinatario_id = %s AND leido = false",
        (usuario_id,), one=True
    )
    return result['count'] if result else 0
