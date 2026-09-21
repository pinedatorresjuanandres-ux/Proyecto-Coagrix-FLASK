from flask import Blueprint, session, redirect, url_for
from controllers.cart_controller import (
    add_to_cart, remove_from_cart, view_cart, checkout, my_orders, order_detail
)

cart_bp = Blueprint('cart', __name__, url_prefix='/carrito')


@cart_bp.before_request
def check_buyer():
    # Solo compradores (Empresa o Comerciante) pueden usar el carrito
    if 'user_id' not in session or session.get('role_name') not in ('Empresa', 'Comerciante'):
        return redirect(url_for('auth.login_page'))


@cart_bp.route('/')
def view_route():
    return view_cart()


@cart_bp.route('/agregar/<int:publicacion_id>', methods=['POST'])
def add_route(publicacion_id):
    return add_to_cart(publicacion_id)


@cart_bp.route('/quitar/<int:publicacion_id>', methods=['POST'])
def remove_route(publicacion_id):
    return remove_from_cart(publicacion_id)


@cart_bp.route('/checkout', methods=['POST'])
def checkout_route():
    return checkout()


@cart_bp.route('/pedidos')
def orders_route():
    return my_orders()


@cart_bp.route('/pedidos/<int:pedido_id>')
def order_detail_route(pedido_id):
    return order_detail(pedido_id)
