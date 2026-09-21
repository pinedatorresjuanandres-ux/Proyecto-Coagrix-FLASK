from flask import render_template, request, redirect, url_for, session, flash, abort
from models.product import get_publication_by_id, decrease_stock
from models.order import create_order, add_order_detail, get_orders_by_user, get_order_details, get_order_for_buyer


def _get_cart():
    return session.setdefault('cart', {})


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

    flash(f"\"{pub['titulo']}\" agregado al carrito.", 'success')
    return redirect(request.referrer or url_for('cart.view_route'))


def remove_from_cart(publicacion_id):
    cart = _get_cart()
    cart.pop(str(publicacion_id), None)
    session.modified = True
    return redirect(url_for('cart.view_route'))


def view_cart():
    cart = _get_cart()
    items = []
    total = 0

    for pub_id_str, cantidad in cart.items():
        pub = get_publication_by_id(int(pub_id_str))
        if not pub:
            continue
        subtotal = float(pub['precio']) * float(cantidad)
        total += subtotal
        items.append({'publication': pub, 'cantidad': cantidad, 'subtotal': subtotal})

    return render_template('cart/view.html', items=items, total=total)


def checkout():
    cart = _get_cart()
    if not cart:
        flash('Tu carrito está vacío.', 'error')
        return redirect(url_for('cart.view_route'))

    items = []
    total = 0
    for pub_id_str, cantidad in cart.items():
        pub = get_publication_by_id(int(pub_id_str))
        if not pub or pub['estado'] != 'Activa':
            continue
        cantidad = min(float(cantidad), float(pub['cantidad_disponible']))
        if cantidad <= 0:
            continue
        subtotal = float(pub['precio']) * cantidad
        total += subtotal
        items.append({'publicacion_id': pub['id'], 'cantidad': cantidad, 'precio': pub['precio']})

    if not items:
        flash('No hay artículos disponibles en tu carrito para pedir.', 'error')
        return redirect(url_for('cart.view_route'))

    pedido_id = create_order(session['user_id'], total)
    if not pedido_id:
        flash('Ocurrió un error al crear el pedido. Intenta de nuevo.', 'error')
        return redirect(url_for('cart.view_route'))

    for item in items:
        add_order_detail(pedido_id, item['publicacion_id'], item['cantidad'], item['precio'])
        decrease_stock(item['publicacion_id'], item['cantidad'])

    session['cart'] = {}
    session.modified = True

    flash('¡Pedido realizado con éxito! El productor lo revisará pronto.', 'success')
    return redirect(url_for('cart.orders_route'))


def my_orders():
    orders = get_orders_by_user(session['user_id'])
    return render_template('cart/orders.html', orders=orders)


def order_detail(pedido_id):
    # Solo el comprador dueño del pedido puede verlo; evita que cambiando
    # el número en la URL alguien vea pedidos ajenos (IDOR).
    order = get_order_for_buyer(pedido_id, session['user_id'])
    if not order:
        abort(403)
    details = get_order_details(pedido_id)
    return render_template('cart/order_detail.html', details=details, pedido_id=pedido_id, order=order)
