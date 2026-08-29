from flask import render_template, request, redirect, url_for, session, flash
from models.message import (
    send_message, get_messages_with_user, get_message_conversations,
    mark_conversation_as_read
)
from models.user import get_user_by_id


def inbox():
    """Lista de conversaciones del usuario logueado."""
    conversations = get_message_conversations(session['user_id'])
    return render_template('messages/inbox.html', conversations=conversations)


def conversation(otro_usuario_id):
    """Chat con un usuario específico: muestra el historial y permite enviar
    un nuevo mensaje."""
    otro_usuario = get_user_by_id(otro_usuario_id)

    if not otro_usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('message.inbox_route'))

    if otro_usuario_id == session['user_id']:
        flash('No puedes enviarte mensajes a ti mismo.', 'error')
        return redirect(url_for('message.inbox_route'))

    if request.method == 'POST':
        contenido = (request.form.get('contenido') or '').strip()
        if contenido:
            send_message(session['user_id'], otro_usuario_id, contenido)
        else:
            flash('Escribe un mensaje antes de enviarlo.', 'error')
        return redirect(url_for('message.conversation_route', otro_usuario_id=otro_usuario_id))

    messages = get_messages_with_user(session['user_id'], otro_usuario_id)
    # Al abrir la conversación, marcamos como leídos los mensajes que nos envió
    mark_conversation_as_read(otro_usuario_id, session['user_id'])

    return render_template('messages/conversation.html',
                            messages=messages,
                            otro_usuario=otro_usuario)
