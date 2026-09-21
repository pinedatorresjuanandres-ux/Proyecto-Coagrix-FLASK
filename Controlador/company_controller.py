from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from Modelo.product import (
    get_active_publications, get_all_categories,
    get_products_with_history, get_price_history_by_product, get_price_comparison
)
from Modelo.user import get_company_data
from Modelo.company import get_company_profile, update_company_profile
from Modelo.user import get_user_by_email, update_user_profile
from database import query_db

company_bp = Blueprint('company', __name__, url_prefix='/company')


@company_bp.before_request
def check_company():
    if 'user_id' not in session or session.get('role_name') != 'Empresa':
        return redirect(url_for('auth.login_page'))


def dashboard():
    """Company dashboard with catalog and order management"""
    company = get_company_data(session['user_id'])


    recent_orders = query_db("""
        SELECT p.*, COUNT(dp.id) as items_count
        FROM pedidos p
        LEFT JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        WHERE p.usuario_id = %s
        GROUP BY p.id
        ORDER BY p.fecha_pedido DESC
        LIMIT 5
    """, (session['user_id'],))

    favorites = query_db("""
        SELECT p.*, pr.nombre as producto_nombre
        FROM favoritos f
        JOIN publicaciones p ON f.publicacion_id = p.id
        JOIN productos pr ON p.producto_id = pr.id
        WHERE f.usuario_id = %s
    """, (session['user_id'],))

    return render_template('company/dashboard.html',
                         company=company,
                         recent_orders=recent_orders,
                         favorites=favorites)


def search_products():
    """Search and filter products for companies"""
    filters = {}
    for key in ('buscar', 'categoria', 'municipio', 'unidad', 'transporte', 'precio_min', 'precio_max', 'orden'):
        value = request.args.get(key)
        if value:
            filters[key] = value
    publications = get_active_publications(filters, price_field='precio_empresa')
    categories = get_all_categories()
    municipios = query_db("SELECT DISTINCT municipio FROM ubicaciones WHERE municipio IS NOT NULL")
    unidades = query_db("SELECT DISTINCT unidad_medida FROM publicaciones WHERE unidad_medida IS NOT NULL")

    return render_template('company/search.html',
                         publications=publications,
                         categories=categories, municipios=municipios,
                         unidades=unidades, filters=filters)




def compare_prices():
    # Sin búsqueda no se lista nada (None): primero se elige qué producto comparar.
    buscar = (request.args.get('buscar') or '').strip()
    price_comparison = (get_price_comparison('precio_empresa', buscar)
                        if buscar or request.args.get('todos') else None)

    productos = get_products_with_history()
    producto_id = request.args.get('producto_id', type=int)
    historial = None
    producto_seleccionado = None

    if producto_id:
        historial = get_price_history_by_product(producto_id, tipo_precio='empresa')
        producto_seleccionado = next((p for p in productos if p['id'] == producto_id), None)

    return render_template('company/compare.html',
                         price_comparison=price_comparison,
                         buscar=buscar,
                         productos=productos,
                         historial=historial,
                         producto_seleccionado=producto_seleccionado,
                         producto_id=producto_id)


@company_bp.route('/dashboard')
def dashboard_route():
    return dashboard()


@company_bp.route('/buscar')
def search_route():
    return search_products()


@company_bp.route('/comparar')
def compare_route():
    return compare_prices()


@company_bp.route('/perfil', methods=['GET', 'POST'])
def profile_route():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        existing = get_user_by_email(email)
        if not nombre or not email or (existing and existing['id'] != session['user_id']):
            flash('Ingresa un nombre y un correo disponible.', 'error')
            return redirect(url_for('company.profile_route'))
        telefono = request.form.get('telefono')
        nit = request.form.get('nit')
        sector = request.form.get('sector')
        update_company_profile(session['user_id'], telefono, nit, sector)
        update_user_profile(session['user_id'], nombre, email)
        session['user_name'] = nombre
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('company.profile_route'))

    company = get_company_profile(session['user_id'])
    return render_template('company/profile.html', company=company)
