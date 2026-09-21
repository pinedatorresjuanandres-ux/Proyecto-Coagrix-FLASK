from flask import render_template, request, session, redirect, url_for, flash, jsonify
from models.product import get_active_publications, get_all_categories, get_publication_by_id
from models.user import get_farmer_data
from models.favorite import is_favorite, toggle_favorite, get_user_favorites
from models.review import get_reviews_for_publication, get_average_rating, create_review, user_has_reviewed
from database import query_db


def catalog():
    """Display product catalog based on user role"""
    filters = {}

    for key in ('categoria', 'municipio', 'unidad', 'transporte', 'precio_min', 'precio_max'):
        value = request.args.get(key)
        if value:
            filters[key] = value
    if request.args.get('buscar'):
        filters['buscar'] = request.args.get('buscar')

    page = request.args.get('page', 1, type=int) or 1
    per_page = 12
    publications, total = get_active_publications(filters, page=page, per_page=per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)

    categories = get_all_categories()

    municipios = query_db("SELECT DISTINCT municipio FROM ubicaciones WHERE municipio IS NOT NULL")
    unidades = query_db("SELECT DISTINCT unidad_medida FROM publicaciones WHERE unidad_medida IS NOT NULL")

    # IDs de favoritos del usuario actual, para pintar el corazón ♥ ya
    # marcado en las tarjetas del catálogo (botón dinámico vía AJAX).
    favorite_ids = set()
    if session.get('user_id'):
        favorite_ids = {fav['id'] for fav in (get_user_favorites(session['user_id']) or [])}

    return render_template('catalog.html',
                         publications=publications,
                         categories=categories,
                         municipios=municipios,
                         unidades=unidades,
                         filters=filters,
                         page=page,
                         total_pages=total_pages,
                         total_results=total,
                         favorite_ids=favorite_ids)


def product_detail(publicacion_id):
    """Show detailed view of a product"""
    pub = query_db("""
        SELECT p.*, pr.nombre as producto_nombre, c.nombre as categoria_nombre,
               ca.usuario_id as campesino_usuario_id, u.nombre as campesino_nombre,
               ub.departamento, ub.municipio
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        JOIN categorias c ON pr.categoria_id = c.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        LEFT JOIN ubicaciones ub ON ca.ubicacion_id = ub.id
        WHERE p.id = %s
    """, (publicacion_id,), one=True)

    if not pub:
        return "Producto no encontrado", 404

    images = query_db("SELECT * FROM archivos WHERE publicacion_id = %s", (publicacion_id,))

    reviews = get_reviews_for_publication(publicacion_id)
    rating = get_average_rating(publicacion_id)

    favorito = False
    ya_resenio = False
    if session.get('user_id'):
        favorito = is_favorite(session['user_id'], publicacion_id)
        ya_resenio = user_has_reviewed(session['user_id'], publicacion_id)

    return render_template('product_detail.html',
                         publication=pub,
                         images=images,
                         reviews=reviews,
                         rating=rating,
                         favorito=favorito,
                         ya_resenio=ya_resenio)


def toggle_favorite_action(publicacion_id):
    """Agrega/quita una publicación de favoritos (requiere sesión).

    Soporta dos modos:
    - Petición AJAX (fetch, con header `X-Requested-With: fetch`): responde
      en JSON `{favorito: true/false}` sin recargar la página, usada por el
      botón ♡/♥ dinámico (ver static/js/components.js).
    - Envío de formulario clásico: se comporta como antes, con flash +
      redirect, para que la funcionalidad no dependa de JavaScript.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'fetch'

    if 'user_id' not in session:
        if is_ajax:
            return jsonify({'error': 'Debes iniciar sesión para usar favoritos.'}), 401
        flash('Debes iniciar sesión para usar favoritos.', 'error')
        return redirect(url_for('auth.login_page'))

    marcado = toggle_favorite(session['user_id'], publicacion_id)

    if is_ajax:
        return jsonify({'favorito': marcado})

    flash('Agregado a favoritos.' if marcado else 'Quitado de favoritos.', 'success')
    return redirect(request.referrer or url_for('product.detail', publicacion_id=publicacion_id))


def add_review_action(publicacion_id):
    """Crea una reseña para una publicación (un usuario solo puede dejar una
    reseña por publicación)."""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para dejar una reseña.', 'error')
        return redirect(url_for('auth.login_page'))

    if user_has_reviewed(session['user_id'], publicacion_id):
        flash('Ya dejaste una reseña para este producto.', 'error')
        return redirect(url_for('product.detail', publicacion_id=publicacion_id))

    try:
        calificacion = int(request.form.get('calificacion', 0))
    except (TypeError, ValueError):
        calificacion = 0

    comentario = (request.form.get('comentario') or '').strip()

    if calificacion < 1 or calificacion > 5:
        flash('Selecciona una calificación entre 1 y 5 estrellas.', 'error')
        return redirect(url_for('product.detail', publicacion_id=publicacion_id))

    create_review(session['user_id'], publicacion_id, calificacion, comentario)
    flash('¡Gracias por tu reseña!', 'success')
    return redirect(url_for('product.detail', publicacion_id=publicacion_id))
