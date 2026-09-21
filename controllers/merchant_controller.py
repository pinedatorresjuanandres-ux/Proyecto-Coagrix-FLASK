from flask import render_template, session, request
from models.product import (
    get_active_publications, get_all_categories,
    get_products_with_history, get_price_history_by_product
)
from models.user import get_merchant_data
from database import query_db


def dashboard():
    """Merchant dashboard with product catalog"""
    merchant = get_merchant_data(session['user_id'])

    # Get merchant's recent orders
    recent_orders = query_db("""
        SELECT p.*, COUNT(dp.id) as items_count
        FROM pedidos p
        LEFT JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        WHERE p.usuario_id = %s
        GROUP BY p.id
        ORDER BY p.fecha_pedido DESC
        LIMIT 5
    """, (session['user_id'],))

    return render_template('merchant/dashboard.html',
                         merchant=merchant,
                         recent_orders=recent_orders)


def compare_prices():
    
    price_comparison = query_db("""
        SELECT pr.id as producto_id, pr.nombre, MIN(p.precio) as precio_min, MAX(p.precio) as precio_max,
               COUNT(DISTINCT p.campesino_id) as num_vendedores
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        WHERE p.estado = 'Activa'
        GROUP BY pr.id
        ORDER BY pr.nombre ASC
    """)

    # Lista de productos disponibles para elegir en el selector de historial
    productos = get_products_with_history()

    # Si el comerciante seleccionó un producto, traemos su historial de precios
    producto_id = request.args.get('producto_id', type=int)
    historial = None
    producto_seleccionado = None

    if producto_id:
        historial = get_price_history_by_product(producto_id)
        producto_seleccionado = next((p for p in productos if p['id'] == producto_id), None)

    return render_template('merchant/compare.html',
                         price_comparison=price_comparison,
                         productos=productos,
                         historial=historial,
                         producto_seleccionado=producto_seleccionado,
                         producto_id=producto_id)
