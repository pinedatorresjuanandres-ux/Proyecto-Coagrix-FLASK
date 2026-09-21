from flask import Blueprint, session, redirect, url_for
from controllers.admin_controller import (
    dashboard, users_list, user_detail, toggle_user, remove_user,
    publications_list, approve_publication, reject_publication, delete_publication_route_action
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    if 'user_id' not in session or session.get('role_name') != 'Administrador':
        return redirect(url_for('auth.login_page'))

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
