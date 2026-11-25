"""Controlador de mensajería interna entre usuarios."""
from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify

from Modelo.message import (
    send_message, get_messages_with_user, get_message_conversations,
    mark_conversation_as_read, ensure_chat_schema, get_message, message_in_conversation,
    edit_message, delete_message_for_everyone, delete_message_for_user, clear_conversation,
    EDIT_WINDOW_MINUTES, MAX_MESSAGE_LENGTH
)
from Modelo.user import get_user_by_id, get_buyers
from Modelo.appointment import get_appointments_between

message_bp = Blueprint('message', __name__, url_prefix='/mensajes')


@message_bp.before_request
def check_login():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    ensure_chat_schema()


def _iso(value):
    return value.strftime('%Y-%m-%dT%H:%M:%S') if hasattr(value, 'strftime') else (str(value) if value else None)


def serialize_message(m, user_id, otro_nombre):
    """Mensaje listo para el navegador. Si fue eliminado para todos, el
    contenido nunca sale del servidor."""
    mio = m['remitente_id'] == user_id
    eliminado = bool(m.get('eliminado_para_todos'))
    respuesta = None
    if m.get('respuesta_a_id'):
        resp_eliminado = bool(m.get('respuesta_eliminado'))
        respuesta = {
            'id': m['respuesta_a_id'],
            'autor': 'Tú' if m.get('respuesta_remitente_id') == user_id else otro_nombre,
            'contenido': '' if resp_eliminado else (m.get('respuesta_contenido') or '')[:140],
            'eliminado': resp_eliminado,
        }
    return {
        'id': m['id'],
        'mio': mio,
        'contenido': '' if eliminado else m['contenido'],
        'fecha': _iso(m['fecha']),
        'editado': bool(m.get('editado_en')) and not eliminado,
        'eliminado': eliminado,
        'leido': bool(m.get('leido')),
        'puede_editar': mio and not eliminado and (m.get('minutos') or 0) < EDIT_WINDOW_MINUTES,
        'respuesta': respuesta,
    }


def serialize_conversations(conversations):
    return [{
        'otro_usuario_id': c['otro_usuario_id'],
        'nombre': c['nombre'],
        'email': c['email'],
        'ultima_fecha': _iso(c['ultima_fecha']),
        'ultimo_mensaje': c['ultimo_mensaje'] or '',
        'no_leidos': int(c['no_leidos'] or 0),
        'fijado': bool(c.get('fijado')),
    } for c in conversations or []]


def _chat_payload(user_id, otro_usuario):
    messages = get_messages_with_user(user_id, otro_usuario['id'])
    return {
        'messages': [serialize_message(m, user_id, otro_usuario['nombre']) for m in messages],
        'conversations': serialize_conversations(get_message_conversations(user_id)),
    }


def split_appointments(appointments):
    """(última cita agendada, historial). La última es la que se creó más
    recientemente y se muestra en el chat; el historial (opción del menú ⋮)
    trae todas, de la fecha más lejana a la más antigua."""
    if not appointments:
        return None, []
    latest = max(appointments, key=lambda c: c['id'])
    history = sorted(appointments, key=lambda c: (str(c['fecha']), str(c['hora'])), reverse=True)
    return latest, history


def _clean_content(raw):
    """Texto del mensaje sin espacios sobrantes, o None si está vacío."""
    contenido = (raw or '').strip()
    return contenido or None


def _json_error(message, status):
    return jsonify(error=message), status


def _other_user_or_error(otro_usuario_id):
    """(usuario, None) o (None, respuesta de error) para las rutas JSON."""
    otro_usuario = get_user_by_id(otro_usuario_id)
    if not otro_usuario:
        return None, _json_error('Usuario no encontrado.', 404)
    if otro_usuario_id == session['user_id']:
        return None, _json_error('No puedes enviarte mensajes a ti mismo.', 400)
    return otro_usuario, None


def inbox():
    """Lista de conversaciones del usuario logueado."""
    filters = {key: request.args.get(key) for key in ('estado',) if request.args.get(key)}
    conversations = get_message_conversations(session['user_id'], filters)
    unread_count = sum(c.get('no_leidos', 0) for c in conversations or [])
    return render_template('messages/inbox.html', conversations=conversations, filters=filters,
                           unread_count=unread_count)


def conversation(otro_usuario_id):
    """Chat con un usuario específico. El envío, la edición y el borrado los
    hace el navegador con las rutas JSON de abajo; el POST de aquí queda como
    respaldo si JavaScript no carga."""
    otro_usuario = get_user_by_id(otro_usuario_id)

    if not otro_usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('message.inbox_route'))

    if otro_usuario_id == session['user_id']:
        flash('No puedes enviarte mensajes a ti mismo.', 'error')
        return redirect(url_for('message.inbox_route'))

    if request.method == 'POST':
        contenido = _clean_content(request.form.get('contenido'))
        if not contenido:
            flash('Escribe un mensaje antes de enviarlo.', 'error')
        elif len(contenido) > MAX_MESSAGE_LENGTH:
            flash(f'El mensaje no puede superar {MAX_MESSAGE_LENGTH} caracteres.', 'error')
        else:
            send_message(session['user_id'], otro_usuario_id, contenido)
        return redirect(url_for('message.conversation_route', otro_usuario_id=otro_usuario_id))

    mark_conversation_as_read(otro_usuario_id, session['user_id'])
    latest_appointment, appointment_history = split_appointments(
        get_appointments_between(session['user_id'], otro_usuario_id))

    return render_template('messages/conversation.html',
                            chat_data=_chat_payload(session['user_id'], otro_usuario),
                            otro_usuario=otro_usuario,
                            latest_appointment=latest_appointment,
                            appointment_history=appointment_history,
                            pending_history=sum(1 for c in appointment_history if c['estado'] == 'Pendiente'),
                            edit_window=EDIT_WINDOW_MINUTES,
                            max_length=MAX_MESSAGE_LENGTH,
                            tomorrow=(date.today() + timedelta(days=1)).isoformat())

def contacts():
    """Lista de comerciantes y empresas para que un campesino inicie una
    conversación con ellos. Exclusivo del rol Campesino: si otro rol llega
    a esta ruta (manualmente o por URL), se corta con 403."""
    if session.get('role_name') != 'Campesino':
        abort(403)
    buyers = get_buyers()
    return render_template('messages/contacts.html', buyers=buyers)


@message_bp.route('/')
def inbox_route():
    return inbox()


@message_bp.route('/contactos')
def contacts_route():
    return contacts()


@message_bp.route('/<int:otro_usuario_id>', methods=['GET', 'POST'])
def conversation_route(otro_usuario_id):
    return conversation(otro_usuario_id)


# ---- API JSON del chat (la usa static/js/chat.js) ----------------------------

@message_bp.route('/<int:otro_usuario_id>/lista')
def list_route(otro_usuario_id):
    """Estado actual del chat. Se consulta cada pocos segundos: al llamarla
    con el chat abierto, lo recibido se marca como leído (✓✓ azul en el otro lado)."""
    otro_usuario, error = _other_user_or_error(otro_usuario_id)
    if error:
        return error
    mark_conversation_as_read(otro_usuario_id, session['user_id'])
    return jsonify(_chat_payload(session['user_id'], otro_usuario))


@message_bp.route('/<int:otro_usuario_id>/enviar', methods=['POST'])
def send_route(otro_usuario_id):
    user_id = session['user_id']
    otro_usuario, error = _other_user_or_error(otro_usuario_id)
    if error:
        return error
    contenido = _clean_content(request.form.get('contenido'))
    if not contenido:
        return _json_error('Escribe un mensaje antes de enviarlo.', 400)
    if len(contenido) > MAX_MESSAGE_LENGTH:
        return _json_error(f'El mensaje no puede superar {MAX_MESSAGE_LENGTH} caracteres.', 400)

    respuesta_a_id = request.form.get('respuesta_a_id', type=int)
    if respuesta_a_id and not message_in_conversation(respuesta_a_id, user_id, otro_usuario_id):
        respuesta_a_id = None

    if not send_message(user_id, otro_usuario_id, contenido, respuesta_a_id):
        return _json_error('No fue posible enviar el mensaje.', 500)
    return jsonify(_chat_payload(user_id, otro_usuario))


def _own_message_or_error(mensaje_id, need_author):
    """Mensaje al que el usuario logueado tiene acceso, o error JSON.
    `need_author=True` exige que sea el autor (editar / borrar para todos)."""
    user_id = session['user_id']
    mensaje = get_message(mensaje_id)
    participa = mensaje and user_id in (mensaje['remitente_id'], mensaje['destinatario_id'])
    if not participa:
        return None, _json_error('Mensaje no encontrado.', 404)
    if need_author and mensaje['remitente_id'] != user_id:
        return None, _json_error('Solo puedes modificar tus propios mensajes.', 403)
    return mensaje, None


def _other_id(mensaje, user_id):
    return mensaje['destinatario_id'] if mensaje['remitente_id'] == user_id else mensaje['remitente_id']


@message_bp.route('/mensaje/<int:mensaje_id>/editar', methods=['POST'])
def edit_route(mensaje_id):
    user_id = session['user_id']
    mensaje, error = _own_message_or_error(mensaje_id, need_author=True)
    if error:
        return error
    if mensaje['eliminado_para_todos']:
        return _json_error('No puedes editar un mensaje eliminado.', 400)
    if (mensaje.get('minutos') or 0) >= EDIT_WINDOW_MINUTES:
        return _json_error(f'Solo puedes editar un mensaje durante los primeros {EDIT_WINDOW_MINUTES} minutos.', 400)
    contenido = _clean_content(request.form.get('contenido'))
    if not contenido:
        return _json_error('El mensaje no puede quedar vacío.', 400)
    if len(contenido) > MAX_MESSAGE_LENGTH:
        return _json_error(f'El mensaje no puede superar {MAX_MESSAGE_LENGTH} caracteres.', 400)
    if contenido != mensaje['contenido'] and not edit_message(mensaje_id, contenido):
        return _json_error('No fue posible editar el mensaje.', 500)
    return jsonify(_chat_payload(user_id, get_user_by_id(_other_id(mensaje, user_id))))


@message_bp.route('/mensaje/<int:mensaje_id>/eliminar', methods=['POST'])
def delete_route(mensaje_id):
    """`modo=mi` lo oculta solo para quien lo pide; `modo=todos` (solo el
    autor) borra el contenido para ambos."""
    user_id = session['user_id']
    modo = request.form.get('modo', 'mi')
    if modo not in ('mi', 'todos'):
        return _json_error('Opción de borrado inválida.', 400)
    mensaje, error = _own_message_or_error(mensaje_id, need_author=(modo == 'todos'))
    if error:
        return error
    ok = (delete_message_for_everyone(mensaje_id) if modo == 'todos'
          else delete_message_for_user(mensaje, user_id))
    if not ok:
        return _json_error('No fue posible eliminar el mensaje.', 500)
    return jsonify(_chat_payload(user_id, get_user_by_id(_other_id(mensaje, user_id))))


@message_bp.route('/<int:otro_usuario_id>/vaciar', methods=['POST'])
def clear_route(otro_usuario_id):
    """Vacía el historial solo para el usuario logueado (el otro lo conserva)."""
    otro_usuario, error = _other_user_or_error(otro_usuario_id)
    if error:
        return error
    if not clear_conversation(session['user_id'], otro_usuario_id):
        return _json_error('No fue posible vaciar la conversación.', 500)
    return jsonify(_chat_payload(session['user_id'], otro_usuario))
