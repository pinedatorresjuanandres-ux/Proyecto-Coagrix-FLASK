import logging
import os

from flask import Flask, render_template, session, url_for, request
from flask_session import Session
from flask_wtf import CSRFProtect

from config import Config
from extensions import limiter
<<<<<<< HEAD
from Controlador.auth_controller import auth_bp
from Controlador.farmer_controller import farmer_bp
from Controlador.admin_controller import admin_bp
from Controlador.company_controller import company_bp
from Controlador.merchant_controller import merchant_bp
from Controlador.product_controller import product_bp
from Controlador.message_controller import message_bp
from Controlador.cart_controller import cart_bp
from Controlador.appointment_controller import appointment_bp
from Controlador.account_controller import account_bp
from Controlador.comment_controller import comment_bp
from Modelo.comment import get_public_comments, get_user_comment

app = Flask(__name__, template_folder='Vista')
app.config.from_object(Config)


Session(app)

csrf = CSRFProtect(app)
=======
from routes.auth_routes import auth_bp
from routes.farmer_routes import farmer_bp
from routes.admin_routes import admin_bp
from routes.company_routes import company_bp
from routes.merchant_routes import merchant_bp
from routes.product_routes import product_bp
from routes.message_routes import message_bp
from routes.cart_routes import cart_bp
from routes.api_routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Session
Session(app)

# Protección CSRF global: exige un token válido en todo POST/PUT/PATCH/DELETE
# que llegue por formulario. Los templates ya incluyen
# {{ csrf_token() }} en cada <form method="POST">.
csrf = CSRFProtect(app)

# Limita intentos de login/registro para dificultar ataques de fuerza bruta.
# La instancia vive en extensions.py para que routes/auth_routes.py pueda
# importarla con el decorador @limiter.limit(...) sin import circular.
>>>>>>> fc18076200e88370b8ec4873b2330482c2206dc0
limiter.init_app(app)

if not app.debug:
    logging.basicConfig(level=logging.INFO)


@app.template_filter('cop')
def format_cop(value):
    """Formatea un número como pesos colombianos: 25000 -> '$25.000 COP'."""
    try:
        entero = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    formateado = f"{entero:,}".replace(',', '.')
    return f"${formateado} COP"


@app.template_global('product_image_url')
def product_image_url(imagen):
    """Devuelve la URL de la imagen del producto, o la imagen por defecto
    si el campesino no subió ninguna."""
    if imagen:
        return url_for('static', filename=imagen)
    return url_for('static', filename='img/default_product.png')


@app.context_processor
def inject_unread_messages():
    """Pone 'unread_messages_count' disponible en cualquier plantilla, para
    mostrar la insignia de mensajes sin leer en el header sin repetir la
    consulta en cada controlador."""
    if session.get('user_id'):
<<<<<<< HEAD
        from Modelo.message import get_unread_count
        return {'unread_messages_count': get_unread_count(session['user_id'])}
    return {'unread_messages_count': 0}

=======
        from models.message import get_unread_count
        return {'unread_messages_count': get_unread_count(session['user_id'])}
    return {'unread_messages_count': 0}

# Register Blueprints
>>>>>>> fc18076200e88370b8ec4873b2330482c2206dc0
app.register_blueprint(auth_bp)
app.register_blueprint(farmer_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)
app.register_blueprint(merchant_bp)
app.register_blueprint(product_bp)
app.register_blueprint(message_bp)
app.register_blueprint(cart_bp)
<<<<<<< HEAD
app.register_blueprint(appointment_bp)
app.register_blueprint(account_bp)
app.register_blueprint(comment_bp)
=======
app.register_blueprint(api_bp)
# La API móvil usa token Bearer, no formularios/cookies; las rutas web
# existentes continúan protegidas por CSRF.
csrf.exempt(api_bp)
>>>>>>> fc18076200e88370b8ec4873b2330482c2206dc0


@app.after_request
def add_no_cache_headers(response):
    """Evita que el navegador guarde en caché las páginas que dependen de
    la sesión (paneles, dashboards, etc.). Sin esto, al cerrar sesión y
    presionar 'atrás', el navegador puede mostrar una copia guardada de
    la página anterior en lugar de pedirla de nuevo al servidor, dando
    la falsa impresión de que la sesión sigue activa."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
<<<<<<< HEAD
=======
    # React Native no usa cookies web; estas cabeceras permiten consumir la
    # API desde el emulador o teléfono durante el desarrollo local.
    if request.path.startswith('/api/'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
>>>>>>> fc18076200e88370b8ec4873b2330482c2206dc0
    return response

@app.route('/')
def index():
<<<<<<< HEAD
    user_id = session.get('user_id')
    return render_template(
        'index.html',
        comentarios=get_public_comments(),
        mi_comentario=get_user_comment(user_id) if user_id else None,
    )


@app.route('/terminos-y-condiciones')
def terms_page():
    return render_template('legal/terminos.html')


@app.route('/politica-de-privacidad')
def privacy_page():
    return render_template('legal/privacidad.html')
=======
    return render_template('index.html')
>>>>>>> fc18076200e88370b8ec4873b2330482c2206dc0


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(400)
def bad_request_error(error):
<<<<<<< HEAD
=======
    # También captura los CSRFError de Flask-WTF (heredan de BadRequest).
>>>>>>> fc18076200e88370b8ec4873b2330482c2206dc0
    return render_template('errors/400.html', reason=getattr(error, 'description', None)), 400


@app.errorhandler(500)
def internal_error(error):
    app.logger.exception('Error interno no controlado')
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=Config.DEBUG, port=port)
