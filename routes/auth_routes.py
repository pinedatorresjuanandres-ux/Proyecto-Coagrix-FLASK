from flask import Blueprint, render_template
from controllers.auth_controller import login, logout, register, forgot_password, reset_password
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

# Límites de intentos para dificultar fuerza bruta / creación masiva de
# cuentas. Flask-Limiter espera un único string con reglas separadas por
# ";" cuando se combinan varias ventanas de tiempo.
LOGIN_LIMITS = "10 per minute;30 per hour"
REGISTER_LIMITS = "5 per minute;20 per hour"
# Límite más estricto: cada solicitud dispara (o intentaría disparar) un
# correo, así que hay que dificultar que alguien los use para saturar
# bandejas de entrada ajenas o para probar por fuerza bruta qué correos
# están registrados.
FORGOT_PASSWORD_LIMITS = "5 per minute;15 per hour"


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit(LOGIN_LIMITS)
def login_page():
    return login()

@auth_bp.route('/login/campesino', methods=['GET', 'POST'])
@limiter.limit(LOGIN_LIMITS)
def login_farmer():
    return login(template='login_agricultor.html')

@auth_bp.route('/login/empresa', methods=['GET', 'POST'])
@limiter.limit(LOGIN_LIMITS)
def login_company():
    return login(template='login_empresa.html')

@auth_bp.route('/login/comerciante', methods=['GET', 'POST'])
@limiter.limit(LOGIN_LIMITS)
def login_merchant():
    return login(template='login_comerciante.html')

@auth_bp.route('/logout')
def logout_action():
    return logout()

@auth_bp.route('/olvide-password', methods=['GET', 'POST'])
@limiter.limit(FORGOT_PASSWORD_LIMITS)
def forgot_password_page():
    return forgot_password()

@auth_bp.route('/restablecer-password/<token>', methods=['GET', 'POST'])
@limiter.limit(FORGOT_PASSWORD_LIMITS)
def reset_password_page(token):
    return reset_password(token)

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_page():
    return register()

@auth_bp.route('/register/campesino', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_farmer():
    return register(template='registro_agricultor.html', default_role_id=2, login_redirect='auth.login_farmer')

@auth_bp.route('/register/empresa', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_company():
    return register(template='registro_empresa.html', default_role_id=3, login_redirect='auth.login_company')

@auth_bp.route('/register/comerciante', methods=['GET', 'POST'])
@limiter.limit(REGISTER_LIMITS)
def register_merchant():
    return register(template='registro_comerciante.html', default_role_id=4, login_redirect='auth.login_merchant')
