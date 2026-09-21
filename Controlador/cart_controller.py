from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from Modelo.product import get_publication_by_id, decrease_stock
from Modelo.order import (
    create_order, add_order_detail, get_orders_by_user, get_order_details, get_order_for_buyer,
    release_order, ESTADOS_CANCELABLES
)

cart_bp = Blueprint('cart', __name__, url_prefix='/carrito')


@cart_bp.before_request
def check_buyer():

    if 'user_id' not in session or session.get('role_name') not in ('Empresa', 'Comerciante'):
        return redirect(url_for('auth.login_page'))


def _get_cart():
    return session.setdefault('cart', {})


def _price_field():
    """Columna de precio que le corresponde al comprador según su rol
    (el acceso al carrito ya está restringido a Empresa/Comerciante)."""
    return 'precio_empresa' if session.get('role_name') == 'Empresa' else 'precio_comerciante'


def add_to_cart(publicacion_id):
    pub = get_publication_by_id(publicacion_id)
    if not pub or pub['estado'] != 'Activa':
        flash('Este producto ya no está disponible.', 'error')
        return redirect(request.referrer or url_for('product.catalog_route'))

    try:
        cantidad = float(request.form.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1

    if cantidad <= 0:
        cantidad = 1
    if cantidad > pub['cantidad_disponible']:
        cantidad = pub['cantidad_disponible']

    cart = _get_cart()
    key = str(publicacion_id)
    cart[key] = cart.get(key, 0) + cantidad
    session.modified = True

    flash(f"\"{pub['titulo']}\" fue agregado al carrito. Revisa el pedido y confírmalo cuando estés listo.", 'success')

    return redirect(url_for('cart.view_route'))


def remove_from_cart(publicacion_id):
    cart = _get_cart()
    cart.pop(str(publicacion_id), None)
    session.modified = True
    return redirect(url_for('cart.view_route'))


def view_cart():
    cart = _get_cart()
    items = []
    total = 0
    price_field = _price_field()

    for pub_id_str, cantidad in cart.items():
        pub = get_publication_by_id(int(pub_id_str))
        if not pub:
            continue
        precio = float(pub[price_field])
        subtotal = precio * float(cantidad)
        total += subtotal
        items.append({'publication': pub, 'precio': precio, 'cantidad': cantidad, 'subtotal': subtotal})

    return render_template('cart/view.html', items=items, total=total)


def checkout():
    """Crea un pedido por cada campesino presente en el carrito (en vez de
    uno solo mezclando productos de varios campesinos). Así cada productor
    solo ve y gestiona (acepta/rechaza/completa) sus propios pedidos, sin
    afectar el estado de los productos de otro campesino que haya estado
    en el mismo carrito."""
    cart = _get_cart()
    if not cart:
        flash('Tu carrito está vacío.', 'error')
        return redirect(url_for('cart.view_route'))

    price_field = _price_field()
    items_por_campesino = {}
    for pub_id_str, cantidad in cart.items():
        pub = get_publication_by_id(int(pub_id_str))
        if not pub or pub['estado'] != 'Activa':
            continue
        cantidad = min(float(cantidad), float(pub['cantidad_disponible']))
        if cantidad <= 0:
            continue
        items_por_campesino.setdefault(pub['campesino_id'], []).append({
            'publicacion_id': pub['id'], 'cantidad': cantidad, 'precio': pub[price_field]
        })

    if not items_por_campesino:
        flash('No hay artículos disponibles en tu carrito para pedir.', 'error')
        return redirect(url_for('cart.view_route'))

    pedidos_creados = 0
    for items in items_por_campesino.values():
        total = sum(float(item['precio']) * item['cantidad'] for item in items)
        pedido_id = create_order(session['user_id'], total)
        if not pedido_id:
            continue
        for item in items:
            add_order_detail(pedido_id, item['publicacion_id'], item['cantidad'], item['precio'])
            decrease_stock(item['publicacion_id'], item['cantidad'])
        pedidos_creados += 1

    session['cart'] = {}
    session.modified = True

    if pedidos_creados == 0:
        flash('Ocurrió un error al crear el pedido. Intenta de nuevo.', 'error')
    elif pedidos_creados > 1:
        flash(f'¡Se crearon {pedidos_creados} pedidos, uno por cada productor! Cada uno los revisará por separado.', 'success')
    else:
        flash('¡Pedido realizado con éxito! El productor lo revisará pronto.', 'success')
    return redirect(url_for('cart.orders_route'))


def my_orders():
    filters = {key: request.args.get(key) for key in ('estado',) if request.args.get(key)}
    orders = get_orders_by_user(session['user_id'], filters)
    return render_template('cart/orders.html', orders=orders, filters=filters)


def order_detail(pedido_id):

    order = get_order_for_buyer(pedido_id, session['user_id'])
    if not order:
        abort(403)
    details = get_order_details(pedido_id)
    return render_template('cart/order_detail.html', details=details, pedido_id=pedido_id, order=order)


def cancel_order(pedido_id):
    """Cancela un pedido del comprador y devuelve el stock a las
    publicaciones (ver `release_order`). Solo se puede cancelar mientras el
    pedido esté Pendiente o Aceptado."""
    if not get_order_for_buyer(pedido_id, session['user_id']):
        abort(403)
    if release_order(pedido_id, 'Cancelado', ESTADOS_CANCELABLES, usuario_id=session['user_id']):
        flash(f'Pedido #{pedido_id} cancelado. Los productos volvieron a estar disponibles.', 'success')
    else:
        flash('Este pedido ya no se puede cancelar.', 'error')
    return redirect(request.referrer or url_for('cart.orders_route'))


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


@cart_bp.route('/pedidos/<int:pedido_id>/cancelar', methods=['POST'])
def cancel_route(pedido_id):
    return cancel_order(pedido_id)
