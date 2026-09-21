from database import query_db, execute_db

# Minutos que tiene el autor para editar un mensaje ya enviado (como en WhatsApp).
EDIT_WINDOW_MINUTES = 15
MAX_MESSAGE_LENGTH = 2000

# Columnas que agrega el chat completo (editar / eliminar / responder).
_CHAT_COLUMNS = {
    'editado_en': "TIMESTAMP NULL DEFAULT NULL",
    'eliminado_para_todos': "TINYINT(1) NOT NULL DEFAULT 0",
    'oculto_remitente': "TINYINT(1) NOT NULL DEFAULT 0",
    'oculto_destinatario': "TINYINT(1) NOT NULL DEFAULT 0",
    'respuesta_a_id': "INT(11) NULL DEFAULT NULL",
}
_schema_ready = False


def ensure_chat_schema():
    """Agrega a `mensajes` las columnas del chat si todavía no existen.

    Es idempotente y solo consulta la base una vez por proceso, así una base
    de datos ya creada funciona sin correr a mano sql/migracion_chat.sql."""
    global _schema_ready
    if _schema_ready:
        return
    rows = query_db("""SELECT COLUMN_NAME FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'mensajes'""")
    if rows is None:  # sin conexión: se reintenta en la próxima petición
        return
    existentes = {r['COLUMN_NAME'].lower() for r in rows}
    for nombre, definicion in _CHAT_COLUMNS.items():
        if nombre not in existentes:
            execute_db(f"ALTER TABLE mensajes ADD COLUMN {nombre} {definicion}")
    _schema_ready = True


def send_message(remitente_id, destinatario_id, contenido, respuesta_a_id=None):
    if respuesta_a_id:
        query = ("INSERT INTO mensajes (remitente_id, destinatario_id, contenido, respuesta_a_id) "
                 "VALUES (%s, %s, %s, %s)")
        return execute_db(query, (remitente_id, destinatario_id, contenido, respuesta_a_id))
    query = "INSERT INTO mensajes (remitente_id, destinatario_id, contenido) VALUES (%s, %s, %s)"
    return execute_db(query, (remitente_id, destinatario_id, contenido))


_MESSAGE_SELECT = """
    SELECT m.*, TIMESTAMPDIFF(MINUTE, m.fecha, NOW()) AS minutos,
           r.remitente_id AS respuesta_remitente_id, r.contenido AS respuesta_contenido,
           r.eliminado_para_todos AS respuesta_eliminado
    FROM mensajes m LEFT JOIN mensajes r ON r.id = m.respuesta_a_id
"""


def get_message(mensaje_id):
    return query_db(_MESSAGE_SELECT + " WHERE m.id = %s", (mensaje_id,), one=True)


def get_messages_with_user(usuario_id, otro_usuario_id):
    """Mensajes de la conversación que `usuario_id` todavía tiene visibles
    (los que borró 'para mí' o al vaciar el chat no aparecen)."""
    return query_db(_MESSAGE_SELECT + """
        WHERE (m.remitente_id = %s AND m.destinatario_id = %s AND m.oculto_remitente = 0)
           OR (m.remitente_id = %s AND m.destinatario_id = %s AND m.oculto_destinatario = 0)
        ORDER BY m.fecha ASC, m.id ASC
    """, (usuario_id, otro_usuario_id, otro_usuario_id, usuario_id)) or []


def message_in_conversation(mensaje_id, usuario_id, otro_usuario_id):
    """True si el mensaje pertenece al chat entre los dos usuarios."""
    row = query_db("""SELECT id FROM mensajes WHERE id = %s
        AND ((remitente_id = %s AND destinatario_id = %s) OR (remitente_id = %s AND destinatario_id = %s))""",
        (mensaje_id, usuario_id, otro_usuario_id, otro_usuario_id, usuario_id), one=True)
    return row is not None


def edit_message(mensaje_id, contenido):
    return execute_db("UPDATE mensajes SET contenido = %s, editado_en = NOW() WHERE id = %s",
                      (contenido, mensaje_id))


def delete_message_for_everyone(mensaje_id):
    """Borra el contenido de verdad (no solo lo oculta) y deja el aviso 'mensaje eliminado'."""
    return execute_db("UPDATE mensajes SET eliminado_para_todos = 1, contenido = '' WHERE id = %s",
                      (mensaje_id,))


def delete_message_for_user(mensaje, usuario_id):
    columna = 'oculto_remitente' if mensaje['remitente_id'] == usuario_id else 'oculto_destinatario'
    return execute_db(f"UPDATE mensajes SET {columna} = 1 WHERE id = %s", (mensaje['id'],))


def clear_conversation(usuario_id, otro_usuario_id):
    """Oculta para `usuario_id` todo el historial con el otro usuario."""
    ok1 = execute_db("UPDATE mensajes SET oculto_remitente = 1 WHERE remitente_id = %s AND destinatario_id = %s",
                     (usuario_id, otro_usuario_id))
    ok2 = execute_db("UPDATE mensajes SET oculto_destinatario = 1 WHERE remitente_id = %s AND destinatario_id = %s",
                     (otro_usuario_id, usuario_id))
    return bool(ok1) and bool(ok2)


def get_message_conversations(usuario_id, filters=None):
    """Conversaciones, con estado de lectura y última actividad.

    GROUP BY reemplaza el antiguo DISTINCT + ORDER BY m.fecha, que puede
    fallar con MySQL en modo estricto y no permitía filtrar no leídos.
    Solo cuenta los mensajes que el usuario aún tiene visibles.
    """
    filters = filters or {}
    query = """
        SELECT CASE WHEN m.remitente_id = %s THEN m.destinatario_id ELSE m.remitente_id END AS otro_usuario_id,
               u.nombre, u.email, MAX(m.fecha) AS ultima_fecha,
               SUBSTRING_INDEX(GROUP_CONCAT(
                   CASE WHEN m.eliminado_para_todos = 1 THEN '🚫 Mensaje eliminado' ELSE m.contenido END
                   ORDER BY m.fecha DESC, m.id DESC SEPARATOR '\\n'), '\\n', 1) AS ultimo_mensaje,
               SUM(CASE WHEN m.destinatario_id = %s AND m.leido = false AND m.eliminado_para_todos = 0 THEN 1 ELSE 0 END) AS no_leidos
        FROM mensajes m
        JOIN usuarios u ON u.id = CASE WHEN m.remitente_id = %s THEN m.destinatario_id ELSE m.remitente_id END
        WHERE (m.remitente_id = %s AND m.oculto_remitente = 0)
           OR (m.destinatario_id = %s AND m.oculto_destinatario = 0)
        GROUP BY otro_usuario_id, u.nombre, u.email
    """
    params = [usuario_id, usuario_id, usuario_id, usuario_id, usuario_id]
    if filters.get('estado') == 'no_leidos':
        query += " HAVING no_leidos > 0"
    elif filters.get('estado') == 'leidos':
        query += " HAVING no_leidos = 0"
    query += " ORDER BY ultima_fecha DESC"
    conversations = query_db(query, tuple(params))
    if conversations is None:
        return None
    return _pin_admin_conversations(usuario_id, conversations, filters)


def get_pinned_admins(usuario_id):
    """Administradores activos cuyo chat queda fijado para `usuario_id`.
    Para un administrador no se fija nada (no tiene sentido fijarse a sí mismo
    ni a sus colegas)."""
    return query_db("""
        SELECT u.id, u.nombre, u.email
        FROM usuarios u JOIN roles r ON r.id = u.rol_id
        WHERE r.nombre = 'Administrador' AND u.estado = 'Activo' AND u.id <> %s
          AND NOT EXISTS (SELECT 1 FROM usuarios v JOIN roles vr ON vr.id = v.rol_id
                          WHERE v.id = %s AND vr.nombre = 'Administrador')
        ORDER BY u.nombre
    """, (usuario_id, usuario_id)) or []


def _pin_admin_conversations(usuario_id, conversations, filters):
    """Sube al principio el chat de cada administrador y lo marca `fijado`.
    Aparece aunque todavía no haya mensajes, para que todos puedan escribirle.
    Con un filtro de lectura activo solo se fijan los que ya están en el resultado."""
    admins = get_pinned_admins(usuario_id)
    if not admins:
        return conversations
    by_id = {c['otro_usuario_id']: c for c in conversations}
    pinned = []
    for admin in admins:
        conv = by_id.pop(admin['id'], None)
        if conv is None:
            if filters.get('estado'):
                continue
            conv = {'otro_usuario_id': admin['id'], 'nombre': admin['nombre'], 'email': admin['email'],
                    'ultima_fecha': None, 'ultimo_mensaje': None, 'no_leidos': 0}
        conv['fijado'] = True
        pinned.append(conv)
    return pinned + [c for c in conversations if c['otro_usuario_id'] in by_id]

def mark_message_as_read(mensaje_id):
    query = "UPDATE mensajes SET leido = true WHERE id = %s"
    return execute_db(query, (mensaje_id,))

def mark_conversation_as_read(otro_usuario_id, usuario_id):
    """Marca como leídos todos los mensajes que 'otro_usuario_id' le envió
    a 'usuario_id' (se llama al abrir la conversación)."""
    query = "UPDATE mensajes SET leido = true WHERE remitente_id = %s AND destinatario_id = %s AND leido = false"
    return execute_db(query, (otro_usuario_id, usuario_id))

def get_unread_count(usuario_id):
    """Total de mensajes sin leer que ha recibido el usuario (para mostrar
    un contador/insignia en el header). Corre en cada página, así que también
    se asegura de que las columnas del chat existan."""
    ensure_chat_schema()
    result = query_db(
        """SELECT COUNT(*) as count FROM mensajes
           WHERE destinatario_id = %s AND leido = false
             AND eliminado_para_todos = 0 AND oculto_destinatario = 0""",
        (usuario_id,), one=True
    )
    return result['count'] if result else 0
