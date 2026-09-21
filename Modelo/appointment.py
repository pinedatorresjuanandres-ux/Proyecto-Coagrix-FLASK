from database import query_db, execute_db


def create_appointment(solicitante_id, receptor_id, fecha, hora, lugar, motivo, mensaje):
    return execute_db("""INSERT INTO citas
        (solicitante_id, receptor_id, fecha, hora, lugar, motivo, mensaje, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendiente')""",
        (solicitante_id, receptor_id, fecha, hora, lugar, motivo, mensaje))


def get_appointment(cita_id):
    return query_db("""SELECT c.*, s.nombre AS solicitante_nombre, r.nombre AS receptor_nombre
        FROM citas c JOIN usuarios s ON s.id = c.solicitante_id
        JOIN usuarios r ON r.id = c.receptor_id WHERE c.id = %s""", (cita_id,), one=True)


def get_appointments_between(usuario_id, otro_usuario_id):
    return query_db("""SELECT c.*, s.nombre AS solicitante_nombre
        FROM citas c JOIN usuarios s ON s.id = c.solicitante_id
        WHERE (c.solicitante_id = %s AND c.receptor_id = %s)
           OR (c.solicitante_id = %s AND c.receptor_id = %s)
        ORDER BY c.fecha ASC, c.hora ASC""", (usuario_id, otro_usuario_id, otro_usuario_id, usuario_id)) or []


def get_user_appointments(usuario_id):
    return query_db("SELECT * FROM citas WHERE solicitante_id = %s OR receptor_id = %s ORDER BY fecha, hora", (usuario_id, usuario_id)) or []


def user_participates(cita, usuario_id):
    return cita and usuario_id in (cita['solicitante_id'], cita['receptor_id'])


def has_schedule_conflict(usuario_id, otro_usuario_id, fecha, hora):
    """True si alguno de los dos usuarios ya tiene una cita Aceptada en esa
    misma fecha y hora (sin duración en el esquema actual, el conflicto se
    evalúa por coincidencia exacta de horario)."""
    candidate = query_db("""SELECT id FROM citas
        WHERE estado = 'Aceptada' AND fecha = %s AND hora = %s
          AND (solicitante_id IN (%s, %s) OR receptor_id IN (%s, %s))
        LIMIT 1""",
        (fecha, hora, usuario_id, otro_usuario_id, usuario_id, otro_usuario_id), one=True)
    return candidate is not None


def update_appointment_status(cita_id, estado):
    return execute_db("UPDATE citas SET estado = %s, actualizada_en = CURRENT_TIMESTAMP WHERE id = %s", (estado, cita_id))


def accept_appointment(cita_id): return update_appointment_status(cita_id, 'Aceptada')
def reject_appointment(cita_id): return update_appointment_status(cita_id, 'Rechazada')
def cancel_appointment(cita_id): return update_appointment_status(cita_id, 'Cancelada')
def complete_appointment(cita_id): return update_appointment_status(cita_id, 'Completada')


def create_notification(usuario_id, mensaje):
    return execute_db("INSERT INTO notificaciones (usuario_id, mensaje) VALUES (%s, %s)", (usuario_id, mensaje))
