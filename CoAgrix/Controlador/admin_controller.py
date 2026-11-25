from flask import Blueprint, render_template, session, request, redirect, url_for, flash

from Modelo.admin import (
    get_dashboard_stats, get_recent_activity, list_users, get_user_full_detail,
    toggle_user_status, delete_user, get_all_roles,
    list_publications_for_moderation, set_publication_status
)
from Modelo.product import delete_publication
from Modelo.comment import (
    list_comments_for_admin, admin_update_comment, admin_set_comment_status,
    admin_delete_comment, clean_comment_text
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def check_admin():
    if 'user_id' not in session or session.get('role_name') != 'Administrador':
        return redirect(url_for('auth.login_page'))


def dashboard():
    stats = get_dashboard_stats()
    activity = get_recent_activity()
    recent_users = list_users(page=1, per_page=5)[0]
    return render_template('admin/dashboard.html', stats=stats, activity=activity, recent_users=recent_users)


def users_list():
    filters = {}
    for key in ('buscar', 'rol', 'estado'):
        value = request.args.get(key)
        if value:
            filters[key] = value

    page = request.args.get('page', 1, type=int) or 1
    per_page = 20
    users, total = list_users(filters, page=page, per_page=per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)

    roles = get_all_roles()
    return render_template('admin/users.html', users=users, roles=roles, filters=filters,
                            page=page, total_pages=total_pages, total_results=total)


def user_detail(usuario_id):
    user = get_user_full_detail(usuario_id)
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('admin.users_route'))
    return render_template('admin/user_detail.html', user=user)


def toggle_user(usuario_id):
    if usuario_id == session.get('user_id'):
        flash('No puedes desactivar tu propia cuenta.', 'error')
        return redirect(url_for('admin.users_route'))
    nuevo_estado = toggle_user_status(usuario_id)
    if nuevo_estado:
        flash(f'Usuario marcado como {nuevo_estado}.', 'success')
    return redirect(url_for('admin.users_route'))


def remove_user(usuario_id):
    if usuario_id == session.get('user_id'):
        flash('No puedes eliminar tu propia cuenta.', 'error')
        return redirect(url_for('admin.users_route'))
    delete_user(usuario_id)
    flash('Usuario eliminado.', 'success')
    return redirect(url_for('admin.users_route'))


def publications_list():
    filters = {}
    for key in ('buscar', 'estado'):
        value = request.args.get(key)
        if value:
            filters[key] = value

    page = request.args.get('page', 1, type=int) or 1
    per_page = 20
    publications, total = list_publications_for_moderation(filters, page=page, per_page=per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)

    return render_template('admin/publications.html', publications=publications, filters=filters,
                            page=page, total_pages=total_pages, total_results=total)


def approve_publication(publicacion_id):
    set_publication_status(publicacion_id, 'Activa')
    flash('Publicación aprobada.', 'success')
    return redirect(url_for('admin.publications_route'))


def reject_publication(publicacion_id):
    set_publication_status(publicacion_id, 'Inactiva')
    flash('Publicación rechazada / ocultada.', 'success')
    return redirect(url_for('admin.publications_route'))


def delete_publication_route_action(publicacion_id):
    delete_publication(publicacion_id)
    flash('Publicación eliminada.', 'success')
    return redirect(url_for('admin.publications_route'))

@admin_bp.route('/dashboard')
def dashboard_route():
    return dashboard()


@admin_bp.route('/usuarios')
def users_route():
    return users_list()


@admin_bp.route('/usuarios/<int:usuario_id>')
def user_detail_route(usuario_id):
    return user_detail(usuario_id)


@admin_bp.route('/usuarios/<int:usuario_id>/toggle', methods=['POST'])
def toggle_user_route(usuario_id):
    return toggle_user(usuario_id)


@admin_bp.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
def delete_user_route(usuario_id):
    return remove_user(usuario_id)


@admin_bp.route('/publicaciones')
def publications_route():
    return publications_list()


@admin_bp.route('/publicaciones/<int:publicacion_id>/aprobar', methods=['POST'])
def approve_publication_route(publicacion_id):
    return approve_publication(publicacion_id)


@admin_bp.route('/publicaciones/<int:publicacion_id>/rechazar', methods=['POST'])
def reject_publication_route(publicacion_id):
    return reject_publication(publicacion_id)


@admin_bp.route('/publicaciones/<int:publicacion_id>/eliminar', methods=['POST'])
def delete_publication_admin_route(publicacion_id):
    return delete_publication_route_action(publicacion_id)


def comments_list():
    filters = {}
    for key in ('buscar', 'estado'):
        value = request.args.get(key)
        if value:
            filters[key] = value

    page = request.args.get('page', 1, type=int) or 1
    per_page = 20
    comments, total = list_comments_for_admin(filters, page=page, per_page=per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)
    if page > total_pages:  # p. ej. se borró el último comentario de la última página
        page = total_pages
        comments, total = list_comments_for_admin(filters, page=page, per_page=per_page)

    return render_template('admin/comments.html', comments=comments, filters=filters,
                           page=page, total_pages=total_pages, total_results=total)


def _back_to_comments():
    return redirect(request.referrer or url_for('admin.comments_route'))


@admin_bp.route('/comentarios')
def comments_route():
    return comments_list()


@admin_bp.route('/comentarios/<int:comentario_id>/editar', methods=['POST'])
def edit_comment_route(comentario_id):
    texto, error = clean_comment_text(request.form.get('texto'))
    if error:
        flash(error, 'error')
    elif admin_update_comment(comentario_id, texto):
        flash('Comentario actualizado.', 'success')
    else:
        flash('No se pudo actualizar el comentario.', 'error')
    return _back_to_comments()


@admin_bp.route('/comentarios/<int:comentario_id>/estado', methods=['POST'])
def comment_status_route(comentario_id):
    estado = request.form.get('estado')
    if admin_set_comment_status(comentario_id, estado):
        flash('Comentario publicado de nuevo.' if estado == 'Publicado'
              else 'Comentario ocultado de la página de inicio.', 'success')
    else:
        flash('No se pudo cambiar el estado del comentario.', 'error')
    return _back_to_comments()


@admin_bp.route('/comentarios/<int:comentario_id>/eliminar', methods=['POST'])
def delete_comment_route(comentario_id):
    admin_delete_comment(comentario_id)
    flash('Comentario eliminado.', 'success')
    return _back_to_comments()
