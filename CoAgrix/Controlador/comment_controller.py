from flask import Blueprint, redirect, url_for, session, request, flash

from Modelo.comment import save_comment, delete_user_comment, clean_comment_text
from extensions import limiter

comment_bp = Blueprint('comment', __name__, url_prefix='/comentarios')

COMMENT_LIMITS = "5 per minute;30 per hour"


def _back_to_testimonials():
    return redirect(url_for('index') + '#testimonios')


@comment_bp.before_request
def require_login():
    if 'user_id' not in session:
        flash('Inicia sesión para dejar tu comentario.', 'error')
        return redirect(url_for('auth.login_page'))


@comment_bp.route('', methods=['POST'])
@limiter.limit(COMMENT_LIMITS)
def save_route():
    texto, error = clean_comment_text(request.form.get('texto'))
    if error:
        flash(error, 'error')
    elif save_comment(session['user_id'], texto):
        flash('¡Gracias! Tu comentario ya está publicado.', 'success')
    else:
        flash('No pudimos guardar tu comentario. Intenta de nuevo.', 'error')
    return _back_to_testimonials()


@comment_bp.route('/eliminar', methods=['POST'])
@limiter.limit(COMMENT_LIMITS)
def delete_route():
    delete_user_comment(session['user_id'])
    flash('Tu comentario fue eliminado.', 'success')
    return _back_to_testimonials()
