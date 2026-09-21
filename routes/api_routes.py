"""API REST usada por CoAgrix Mobile.

La web original sigue funcionando con sesiones Flask. La aplicación móvil usa
un token firmado, enviado en `Authorization: Bearer <token>`, para no depender
de cookies del navegador.
"""
from functools import wraps
from flask import Blueprint, jsonify, request, current_app, url_for
from datetime import datetime, timedelta
import secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from database import query_db
from models.user import (get_user_by_email, get_user_by_id, create_user, get_role_name,
    create_farmer_profile, create_company_profile, create_merchant_profile,
    verify_password, upgrade_password_if_plaintext, update_password, get_farmer_data)
from models.product import get_all_categories, get_active_publications, get_publication_by_id, decrease_stock
from models.order import create_order, add_order_detail, get_orders_by_user, get_order_for_buyer, get_order_details, update_order_status, order_belongs_to_farmer
from models.favorite import get_user_favorites, toggle_favorite
from models.review import get_reviews_for_publication, get_average_rating, create_review, user_has_reviewed
from models.farmer import get_farmer_publications, get_farmer_orders, update_farmer_profile
from models.company import get_company_profile, update_company_profile
from models.admin import get_dashboard_stats, list_users
from models.message import get_message_conversations, get_messages_with_user, send_message, mark_conversation_as_read
from models.user import set_reset_token
from utils.mailer import send_reset_email

api_bp = Blueprint('api', __name__, url_prefix='/api')

def _jsonable(value):
    if isinstance(value, dict): return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list): return [_jsonable(v) for v in value]
    if hasattr(value, 'isoformat'): return value.isoformat()
    if isinstance(value, (bytes, bytearray)): return value.decode('utf-8', 'replace')
    return value

def response(data=None, status=200, **extra):
    body = {'ok': status < 400, 'data': _jsonable(data)}
    body.update(extra)
    return jsonify(body), status

def payload():
    return request.get_json(silent=True) or {}

def serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='coagrix-mobile')

def make_token(user):
    return serializer().dumps({'id': user['id'], 'role': get_role_name(user['rol_id'])})

def require_auth(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            header = request.headers.get('Authorization', '')
            if not header.startswith('Bearer '): return response(None, 401, error='Inicia sesión para continuar.')
            try:
                token_data = serializer().loads(header[7:], max_age=60 * 60 * 24 * 7)
            except (BadSignature, SignatureExpired):
                return response(None, 401, error='La sesión expiró. Inicia sesión otra vez.')
            user = get_user_by_id(token_data.get('id'))
            if not user or user['estado'] != 'Activo': return response(None, 401, error='Usuario no disponible.')
            user['role_name'] = get_role_name(user['rol_id'])
            if roles and user['role_name'] not in roles: return response(None, 403, error='No tienes permiso para esta acción.')
            request.mobile_user = user
            return fn(*args, **kwargs)
        return wrapped
    return decorator

@api_bp.route('/health')
def health(): return response({'service': 'CoAgrix API', 'version': '1.0'})

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = payload(); email = (data.get('email') or '').strip().lower(); password = data.get('password') or ''
    user = get_user_by_email(email)
    if not user or not verify_password(user['password'], password): return response(None, 401, error='Correo o contraseña incorrectos.')
    if user['estado'] != 'Activo': return response(None, 403, error='La cuenta está inactiva.')
    upgrade_password_if_plaintext(user['id'], user['password'], password)
    user_data = {'id': user['id'], 'nombre': user['nombre'], 'email': user['email'], 'rol': get_role_name(user['rol_id'])}
    return response({'token': make_token(user), 'user': user_data})

@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = payload(); nombre = (data.get('nombre') or '').strip(); email = (data.get('email') or '').strip().lower(); password = data.get('password') or ''
    try: rol_id = int(data.get('rol_id', 4))
    except (TypeError, ValueError): rol_id = 4
    if not nombre or not email or len(password) < 8 or rol_id not in (2, 3, 4): return response(None, 400, error='Completa los datos. La contraseña debe tener mínimo 8 caracteres.')
    if get_user_by_email(email): return response(None, 409, error='Este correo ya está registrado.')
    user_id = create_user(nombre, email, password, rol_id)
    if not user_id: return response(None, 500, error='No fue posible crear la cuenta.')
    {2: create_farmer_profile, 3: create_company_profile, 4: create_merchant_profile}[rol_id](user_id)
    return response({'id': user_id}, 201, message='Cuenta creada. Ya puedes iniciar sesión.')

@api_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Solicita el mismo correo de recuperación que usa el sitio web."""
    email = (payload().get('email') or '').strip().lower(); user = get_user_by_email(email)
    if user:
        token = secrets.token_urlsafe(32)
        set_reset_token(user['id'], token, datetime.now() + timedelta(hours=1))
        link = url_for('auth.reset_password_page', token=token, _external=True)
        send_reset_email(user['email'], user['nombre'], link)
    return response(None, message='Si el correo existe, enviamos las instrucciones para recuperar la contraseña.')

@api_bp.route('/auth/logout', methods=['POST'])
@require_auth()
def logout(): return response(None, message='Sesión cerrada. El teléfono debe eliminar el token almacenado.')

@api_bp.route('/auth/reset-password', methods=['POST'])
@require_auth()
def reset_password():
    new_password = payload().get('password') or ''
    if len(new_password) < 8: return response(None, 400, error='La contraseña debe tener mínimo 8 caracteres.')
    update_password(request.mobile_user['id'], new_password)
    return response(None, message='Contraseña actualizada.')

@api_bp.route('/categories')
def categories(): return response(get_all_categories() or [])

@api_bp.route('/products')
def products():
    filters = {key: request.args.get(key) for key in ('categoria','municipio','unidad','transporte','precio_min','precio_max','buscar') if request.args.get(key)}
    page = request.args.get('page', 1, type=int) or 1
    items, total = get_active_publications(filters, page=max(1, page), per_page=12)
    return response({'items': items or [], 'total': total, 'page': page})

@api_bp.route('/products/<int:publication_id>')
def product_detail(publication_id):
    product = query_db('''SELECT p.*, pr.nombre producto_nombre, c.nombre categoria_nombre, ca.usuario_id campesino_usuario_id, u.nombre campesino_nombre, ub.departamento, ub.municipio FROM publicaciones p JOIN productos pr ON p.producto_id=pr.id JOIN categorias c ON pr.categoria_id=c.id JOIN campesinos ca ON p.campesino_id=ca.id JOIN usuarios u ON ca.usuario_id=u.id LEFT JOIN ubicaciones ub ON ca.ubicacion_id=ub.id WHERE p.id=%s''', (publication_id,), one=True)
    if not product: return response(None, 404, error='Producto no encontrado.')
    product['reviews'] = get_reviews_for_publication(publication_id) or []; product['rating'] = get_average_rating(publication_id)
    return response(product)

@api_bp.route('/favorites', methods=['GET'])
@require_auth()
def favorites(): return response(get_user_favorites(request.mobile_user['id']) or [])

@api_bp.route('/products/<int:publication_id>/favorite', methods=['POST'])
@require_auth()
def favorite(publication_id): return response({'favorite': toggle_favorite(request.mobile_user['id'], publication_id)})

@api_bp.route('/products/<int:publication_id>/reviews', methods=['POST'])
@require_auth()
def review(publication_id):
    data = payload(); rating = data.get('calificacion'); comment = (data.get('comentario') or '').strip()
    try: rating = int(rating)
    except (ValueError, TypeError): rating = 0
    if rating not in range(1, 6): return response(None, 400, error='La calificación debe ser de 1 a 5.')
    if user_has_reviewed(request.mobile_user['id'], publication_id): return response(None, 409, error='Ya calificaste este producto.')
    create_review(request.mobile_user['id'], publication_id, rating, comment)
    return response(None, 201, message='Reseña guardada.')

@api_bp.route('/cart/checkout', methods=['POST'])
@require_auth(('Empresa', 'Comerciante'))
def checkout():
    cart = payload().get('items') or []
    if not cart: return response(None, 400, error='El carrito está vacío.')
    valid = []; total = 0
    for item in cart:
        publication = get_publication_by_id(item.get('publicacion_id'))
        try: quantity = float(item.get('cantidad', 0))
        except (TypeError, ValueError): quantity = 0
        if publication and publication['estado'] == 'Activa' and quantity > 0:
            quantity = min(quantity, float(publication['cantidad_disponible']))
            valid.append((publication, quantity)); total += float(publication['precio']) * quantity
    if not valid: return response(None, 400, error='No hay artículos disponibles.')
    order_id = create_order(request.mobile_user['id'], total)
    if not order_id: return response(None, 500, error='No se pudo crear el pedido.')
    for publication, quantity in valid:
        add_order_detail(order_id, publication['id'], quantity, publication['precio']); decrease_stock(publication['id'], quantity)
    return response({'id': order_id, 'total': total}, 201, message='Pedido creado correctamente.')

@api_bp.route('/orders')
@require_auth()
def orders():
    user = request.mobile_user
    if user['role_name'] == 'Campesino':
        farmer = get_farmer_data(user['id']); return response(get_farmer_orders(farmer['id']) if farmer else [])
    if user['role_name'] in ('Empresa', 'Comerciante'): return response(get_orders_by_user(user['id']) or [])
    return response([], 403, error='El administrador no tiene pedidos.')

@api_bp.route('/orders/<int:order_id>')
@require_auth()
def order_detail(order_id):
    user = request.mobile_user; permitted = bool(get_order_for_buyer(order_id, user['id']))
    if user['role_name'] == 'Campesino':
        farmer = get_farmer_data(user['id']); permitted = bool(farmer and order_belongs_to_farmer(order_id, farmer['id']))
    if not permitted: return response(None, 403, error='No puedes ver este pedido.')
    return response({'order': get_order_for_buyer(order_id, user['id']) or {'id': order_id}, 'items': get_order_details(order_id) or []})

@api_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
@require_auth(('Campesino',))
def order_status(order_id):
    farmer = get_farmer_data(request.mobile_user['id']); status = payload().get('estado')
    if status not in ('Aceptado','Rechazado','Completado') or not farmer or not order_belongs_to_farmer(order_id, farmer['id']): return response(None, 403, error='No puedes actualizar este pedido.')
    update_order_status(order_id, status); return response(None, message='Estado actualizado.')

@api_bp.route('/profile', methods=['GET', 'PUT'])
@require_auth()
def profile():
    user = request.mobile_user
    if request.method == 'GET':
        info = dict(user); info.pop('password', None)
        if user['role_name'] == 'Campesino': info['profile'] = get_farmer_data(user['id'])
        elif user['role_name'] == 'Empresa': info['profile'] = get_company_profile(user['id'])
        return response(info)
    data = payload()
    if user['role_name'] == 'Campesino': update_farmer_profile(user['id'], data.get('telefono'), data.get('descripcion'), data.get('ubicacion_id'))
    elif user['role_name'] == 'Empresa': update_company_profile(user['id'], data.get('telefono'), data.get('nit'), data.get('sector'))
    else: return response(None, 400, error='Este perfil no tiene campos editables en móvil.')
    return response(None, message='Perfil actualizado.')

@api_bp.route('/messages', methods=['GET'])
@require_auth()
def conversations(): return response(get_message_conversations(request.mobile_user['id']) or [])

@api_bp.route('/messages/<int:other_user_id>', methods=['GET', 'POST'])
@require_auth()
def messages(other_user_id):
    if request.method == 'POST':
        content = (payload().get('contenido') or '').strip()
        if not content: return response(None, 400, error='Escribe un mensaje.')
        send_message(request.mobile_user['id'], other_user_id, content)
    mark_conversation_as_read(other_user_id, request.mobile_user['id'])
    return response(get_messages_with_user(request.mobile_user['id'], other_user_id) or [])

@api_bp.route('/admin/dashboard')
@require_auth(('Administrador',))
def admin_dashboard(): return response(get_dashboard_stats())

@api_bp.route('/admin/users')
@require_auth(('Administrador',))
def admin_users(): return response(list_users() or [])
