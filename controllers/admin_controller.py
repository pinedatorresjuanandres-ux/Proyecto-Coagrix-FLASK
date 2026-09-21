from flask import render_template, session, request, redirect, url_for, flash
from models.admin import (
    get_dashboard_stats, get_recent_activity, list_users, get_user_full_detail,
    toggle_user_status, delete_user, get_all_roles,
    list_publications_for_moderation, set_publication_status
)
from models.product import delete_publication


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
