from flask import Blueprint, render_template, session, request, redirect, url_for

from Modelo.product import (
    get_active_publications, get_all_categories,
    get_products_with_history, get_price_history_by_product, get_price_comparison
)
from Modelo.user import get_merchant_data
from database import query_db

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


@merchant_bp.before_request
def check_merchant():
    if 'user_id' not in session or session.get('role_name') != 'Comerciante':
        return redirect(url_for('auth.login_page'))


def dashboard():
    """Merchant dashboard with product catalog"""
    merchant = get_merchant_data(session['user_id'])


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

    # Sin búsqueda no se lista nada (None): primero se elige qué producto comparar.
    buscar = (request.args.get('buscar') or '').strip()
    price_comparison = (get_price_comparison('precio_comerciante', buscar)
                        if buscar or request.args.get('todos') else None)

    productos = get_products_with_history()
    producto_id = request.args.get('producto_id', type=int)
    historial = None
    producto_seleccionado = None

    if producto_id:
        historial = get_price_history_by_product(producto_id, tipo_precio='comerciante')
        producto_seleccionado = next((p for p in productos if p['id'] == producto_id), None)

    return render_template('merchant/compare.html',
                         price_comparison=price_comparison,
                         buscar=buscar,
                         productos=productos,
                         historial=historial,
                         producto_seleccionado=producto_seleccionado,
                         producto_id=producto_id)


@merchant_bp.route('/dashboard')
def dashboard_route():
    return dashboard()


@merchant_bp.route('/comparar')
def compare_route():
    return compare_prices()
