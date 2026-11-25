import re
import threading

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from Modelo.user import (
    get_user_by_email, create_user, get_role_name,
    create_farmer_profile, create_company_profile, create_merchant_profile, create_location,
    verify_password, upgrade_password_if_plaintext
)
from Modelo.ubicaciones import get_ubicaciones_colombia, is_valid_location
from Modelo.password_reset import (
    recent_reset_exists, create_reset_token, is_reset_token_valid, consume_reset_token, TOKEN_MINUTES
)
from extensions import limiter
from mailer import send_email
from config import Config

auth_bp = Blueprint('auth', __name__)


LOGIN_LIMITS = "10 per minute;30 per hour"
REGISTER_LIMITS = "5 per minute;20 per hour"
RESET_LIMITS = "10 per minute;30 per hour"


def _password_error(password, password_confirm):
    """Valida la seguridad mínima de la contraseña de registro. Devuelve
    un mensaje de error si algo no cumple, o None si está todo bien."""
    if not password or len(password) < 8:
        return 'La contraseña debe tener al menos 8 caracteres.'
    if not re.search(r'[A-Z]', password):
        return 'La contraseña debe incluir al menos una letra mayúscula.'
    if password != password_confirm:
        return 'Las contraseñas no coinciden.'
    return None

def _registration_error(nombre, email, telefono, departamento, municipio, role_id, nit=None):
    if not nombre or len(nombre.strip()) < 3 or len(nombre.strip()) > 100:
        return 'Ingresa un nombre válido (3 a 100 caracteres).'
    if not email or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return 'Ingresa un correo electrónico válido.'
    if not telefono or not re.fullmatch(r'[0-9+() -]{7,20}', telefono):
        return 'Ingresa un teléfono válido.'
    if not departamento or not municipio:
        return 'Departamento y municipio son obligatorios.'
    if not is_valid_location(departamento, municipio):
        return 'Selecciona un departamento y un municipio válidos de la lista.'
    if role_id == 3 and (not nit or not re.fullmatch(r'[0-9]{6,12}(-[0-9])?', nit)):
        return 'Ingresa un NIT válido.'
    return None


def login(template='login.html'):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = get_user_by_email(email)

        if user and verify_password(user['password'], password):
            upgrade_password_if_plaintext(user['id'], user['password'], password)

            if user['estado'] == 'Inactivo':
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                return redirect(request.path)

            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['role_id'] = user['rol_id']
            session['role_name'] = get_role_name(user['rol_id'])

            if session['role_name'] == 'Administrador':
                return redirect(url_for('admin.dashboard_route'))
            elif session['role_name'] == 'Campesino':
                return redirect(url_for('farmer.dashboard'))
            elif session['role_name'] == 'Empresa':
                return redirect(url_for('company.dashboard_route'))
            elif session['role_name'] == 'Comerciante':
                return redirect(url_for('merchant.dashboard_route'))
        else:
            flash('Credenciales incorrectas.', 'error')

    return render_template(template)


def logout():
    session.clear()
    return redirect(url_for('index'))


def register(template='registro.html', default_role_id=None, login_redirect='auth.login_page'):
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        telefono = (request.form.get('telefono') or '').strip()
        departamento = (request.form.get('departamento') or '').strip()
        municipio = (request.form.get('municipio') or '').strip()
        direccion = (request.form.get('direccion') or '').strip()
        nit = (request.form.get('nit') or '').strip()
        sector = (request.form.get('sector') or '').strip()
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        rol_id = default_role_id

        error = _password_error(password, password_confirm)
        error = error or _registration_error(nombre, email, telefono, departamento, municipio, int(rol_id) if rol_id else 0, nit)
        if error:
            flash(error, 'error')
            return redirect(request.path)

        if get_user_by_email(email):
            flash('El correo ya está registrado.', 'error')
            return redirect(request.path)

        user_id = create_user(nombre, email, password, rol_id)
        if user_id:

            rol_id_int = int(rol_id) if rol_id else None
            location_id = create_location(departamento, municipio, direccion or None)
            if not location_id:
                flash('No fue posible guardar la ubicación.', 'error')
                return redirect(request.path)
            if rol_id_int == 2:
                create_farmer_profile(user_id, telefono, location_id)
            elif rol_id_int == 3:
                create_company_profile(user_id, nit, telefono, location_id, sector or None)
            elif rol_id_int == 4:
                create_merchant_profile(user_id, telefono, location_id)

            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for(login_redirect))
        else:
            flash('Error al registrar el usuario.', 'error')

    return render_template(template, ubicaciones=get_ubicaciones_colombia())


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit(LOGIN_LIMITS)
def login_page():
    return login()


# Antes había un login por rol; ahora hay uno solo (/login) que detecta el rol
# al validar las credenciales. Estas direcciones antiguas se conservan como
# redirecciones para no romper enlaces o favoritos guardados.
@auth_bp.route('/login/campesino')
@auth_bp.route('/login/empresa')
@auth_bp.route('/login/comerciante')
def login_por_rol_antiguo():
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/logout')
def logout_action():
    return logout()


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_page():
    return register()


@auth_bp.route('/register/campesino', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_farmer():
    return register(template='registro_agricultor.html', default_role_id=2)


@auth_bp.route('/register/empresa', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_company():
    return register(template='registro_empresa.html', default_role_id=3)


@auth_bp.route('/register/comerciante', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_merchant():
    return register(template='registro_comerciante.html', default_role_id=4)


def _reset_link(token):
    """Enlace completo que va en el correo. Usa APP_BASE_URL si está
    configurada; si no, la dirección desde la que se hizo la solicitud."""
    path = url_for('auth.reset_password_page', token=token)
    base = Config.APP_BASE_URL or request.url_root.rstrip('/')
    return base + path


def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        user = get_user_by_email(email) if email else None

        if user and not recent_reset_exists(user['id']):
            token = create_reset_token(user['id'])
            if token:
                body = (
                    f"Hola {user['nombre']},\n\n"
                    "Recibimos una solicitud para restablecer la contraseña de tu cuenta de CoAgrix.\n"
                    f"Entra a este enlace (vence en {TOKEN_MINUTES} minutos y solo sirve una vez):\n\n"
                    f"{_reset_link(token)}\n\n"
                    "Si no fuiste tú, ignora este mensaje: tu contraseña seguirá igual."
                )
                # En un hilo aparte: la respuesta no espera al servidor de correo
                # y tarda igual exista o no el correo (así no se puede averiguar
                # qué correos están registrados).
                threading.Thread(
                    target=send_email,
                    args=(user['email'], 'Restablece tu contraseña - CoAgrix', body),
                    daemon=True
                ).start()

        # Mismo mensaje siempre, exista o no la cuenta.
        flash('Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña. '
              f'Revisa tu bandeja (vence en {TOKEN_MINUTES} minutos).', 'success')
        return redirect(request.path)

    return render_template('olvide_contrasena.html')


def reset_password(token):
    if not is_reset_token_valid(token):
        flash('El enlace no es válido o ya venció. Solicita uno nuevo.', 'error')
        return redirect(url_for('auth.forgot_password_page'))

    if request.method == 'POST':
        error = _password_error(request.form.get('password'), request.form.get('password_confirm'))
        if error:
            flash(error, 'error')
            return redirect(request.path)
        if consume_reset_token(token, request.form.get('password')):
            flash('Contraseña actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login_page'))
        flash('El enlace no es válido o ya venció. Solicita uno nuevo.', 'error')
        return redirect(url_for('auth.forgot_password_page'))

    return render_template('restablecer_contrasena.html')


@auth_bp.route('/olvide-contrasena', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def forgot_password_page():
    return forgot_password()


@auth_bp.route('/restablecer/<token>', methods=['GET', 'POST'])
@limiter.limit(RESET_LIMITS)
def reset_password_page(token):
    return reset_password(token)
