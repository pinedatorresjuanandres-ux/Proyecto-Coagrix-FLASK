from flask import render_template, session
from models.product import get_active_publications, get_all_categories
from models.user import get_company_data
from models.order import get_order_details
from database import query_db

def dashboard():
    """Company dashboard with catalog and order management"""
    company = get_company_data(session['user_id'])
    
    # Get company's recent orders
    recent_orders = query_db("""
        SELECT p.*, COUNT(dp.id) as items_count
        FROM pedidos p
        LEFT JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        WHERE p.usuario_id = %s
        GROUP BY p.id
        ORDER BY p.fecha_pedido DESC
        LIMIT 5
    """, (session['user_id'],))
    
    # Get company's favorites
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
    publications = get_active_publications()
    categories = get_all_categories()
    
    return render_template('company/search.html',
                         publications=publications,
                         categories=categories)
