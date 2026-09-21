from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort
from models.user import get_farmer_data
from models.farmer import get_farmer_publications, get_farmer_orders, get_farmer_sales_stats, update_farmer_profile
from models.order import get_order, update_order_status, get_order_details, order_belongs_to_farmer
from controllers.farmer_controller import create_pub, edit_pub, delete_pub

farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')

@farmer_bp.before_request
def check_farmer():
    if 'user_id' not in session or session.get('role_name') != 'Campesino':
        return redirect(url_for('auth.login_page'))

@farmer_bp.route('/dashboard')
def dashboard():
    farmer = get_farmer_data(session['user_id'])
    stats = get_farmer_sales_stats(farmer['id']) if farmer else None
    return render_template('farmer/dashboard.html', farmer=farmer, stats=stats)

@farmer_bp.route('/perfil', methods=['GET', 'POST'])
def profile():
    farmer = get_farmer_data(session['user_id'])
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        descripcion = request.form.get('descripcion')
        ubicacion_id = farmer['ubicacion_id'] if farmer else None
        update_farmer_profile(session['user_id'], telefono, descripcion, ubicacion_id)
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('farmer.profile'))
    return render_template('farmer/profile.html', farmer=farmer)

@farmer_bp.route('/publicaciones')
def publications():
    farmer = get_farmer_data(session['user_id'])
    pubs = get_farmer_publications(farmer['id']) if farmer else []
    return render_template('farmer/publications.html', publications=pubs)

@farmer_bp.route('/publicaciones/crear', methods=['GET', 'POST'])
def create_publication_route():
    return create_pub()

@farmer_bp.route('/publicaciones/<int:publicacion_id>/editar', methods=['GET', 'POST'])
def edit_publication_route(publicacion_id):
    return edit_pub(publicacion_id)

@farmer_bp.route('/publicaciones/<int:publicacion_id>/eliminar', methods=['POST'])
def delete_publication_route(publicacion_id):
    return delete_pub(publicacion_id)

@farmer_bp.route('/pedidos')
def orders_route():
    farmer = get_farmer_data(session['user_id'])
    orders = get_farmer_orders(farmer['id']) if farmer else []
    return render_template('farmer/orders.html', orders=orders)


def _require_own_order(pedido_id):
    """Devuelve el registro del campesino si el pedido le pertenece
    (contiene al menos una de sus publicaciones); si no, aborta con 403.
    Centraliza el chequeo de propiedad para las 4 rutas de pedidos de
    abajo, en vez de repetirlo en cada una."""
    farmer = get_farmer_data(session['user_id'])
    if not farmer or not order_belongs_to_farmer(pedido_id, farmer['id']):
        abort(403)
    return farmer


@farmer_bp.route('/pedidos/<int:pedido_id>')
def order_detail_route(pedido_id):
    _require_own_order(pedido_id)
    details = get_order_details(pedido_id)
    order = get_order(pedido_id)
    return render_template('farmer/order_detail.html', details=details, order=order)

@farmer_bp.route('/pedidos/<int:pedido_id>/aceptar', methods=['POST'])
def accept_order_route(pedido_id):
    _require_own_order(pedido_id)
    update_order_status(pedido_id, 'Aceptado')
    flash('Pedido aceptado.', 'success')
    return redirect(url_for('farmer.orders_route'))

@farmer_bp.route('/pedidos/<int:pedido_id>/rechazar', methods=['POST'])
def reject_order_route(pedido_id):
    _require_own_order(pedido_id)
    update_order_status(pedido_id, 'Rechazado')
    flash('Pedido rechazado.', 'success')
    return redirect(url_for('farmer.orders_route'))

@farmer_bp.route('/pedidos/<int:pedido_id>/completar', methods=['POST'])
def complete_order_route(pedido_id):
    _require_own_order(pedido_id)
    update_order_status(pedido_id, 'Completado')
    flash('Pedido marcado como completado.', 'success')
    return redirect(url_for('farmer.orders_route'))
