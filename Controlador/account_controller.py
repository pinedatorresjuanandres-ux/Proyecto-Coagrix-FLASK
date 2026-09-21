from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from Modelo.user import get_user_by_email, get_user_by_id, update_user_profile, verify_password, update_user_password
from Controlador.auth_controller import _password_error
from Modelo.merchant import get_merchant_profile, update_merchant_profile

account_bp = Blueprint('account', __name__, url_prefix='/cuenta')

@account_bp.before_request
def require_login():
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))

@account_bp.route('/perfil', methods=['GET', 'POST'])
def profile_route():
    user_id = session['user_id']
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        existing = get_user_by_email(email)
        if not nombre or not email or (existing and existing['id'] != user_id):
            flash('Ingresa un nombre y un correo disponible.', 'error')
            return redirect(url_for('account.profile_route'))
        update_user_profile(user_id, nombre, email)
        if session.get('role_name') == 'Comerciante':
            update_merchant_profile(user_id, (request.form.get('telefono') or '').strip() or None)
        session['user_name'] = nombre
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('account.profile_route'))
    user = get_user_by_id(user_id)
    merchant = get_merchant_profile(user_id) if session.get('role_name') == 'Comerciante' else None
    return render_template('account/profile.html', user=user, merchant=merchant)


@account_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
def change_password_route():
    if request.method == 'POST':
        user = get_user_by_id(session['user_id'])
        actual = request.form.get('password_actual') or ''
        nueva = request.form.get('password')
        if not user or not verify_password(user['password'], actual):
            flash('La contraseña actual no es correcta.', 'error')
        elif actual == nueva:
            flash('La nueva contraseña debe ser distinta de la actual.', 'error')
        else:
            error = _password_error(nueva, request.form.get('password_confirm'))
            if error:
                flash(error, 'error')
            else:
                update_user_password(user['id'], nueva)
                flash('Contraseña actualizada correctamente.', 'success')
                return redirect(url_for('account.profile_route'))
        return redirect(url_for('account.change_password_route'))
    return render_template('account/change_password.html')
