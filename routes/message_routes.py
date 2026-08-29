from flask import Blueprint, session, redirect, url_for
from controllers.message_controller import inbox, conversation

message_bp = Blueprint('message', __name__, url_prefix='/mensajes')


@message_bp.before_request
def check_login():
    # Cualquier usuario logueado (de cualquier rol) puede usar el chat
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))


@message_bp.route('/')
def inbox_route():
    return inbox()


@message_bp.route('/<int:otro_usuario_id>', methods=['GET', 'POST'])
def conversation_route(otro_usuario_id):
    return conversation(otro_usuario_id)
