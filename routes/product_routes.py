from flask import Blueprint
from controllers.product_controller import (
    catalog, product_detail, toggle_favorite_action, add_review_action
)
from controllers.favorite_controller import list_favorites

product_bp = Blueprint('product', __name__, url_prefix='/productos')

@product_bp.route('/catalogo')
def catalog_route():
    return catalog()

@product_bp.route('/<int:publicacion_id>')
def detail(publicacion_id):
    return product_detail(publicacion_id)

@product_bp.route('/<int:publicacion_id>/favorito', methods=['POST'])
def favorite_route(publicacion_id):
    return toggle_favorite_action(publicacion_id)

@product_bp.route('/<int:publicacion_id>/resena', methods=['POST'])
def review_route(publicacion_id):
    return add_review_action(publicacion_id)

@product_bp.route('/favoritos')
def favorites_route():
    return list_favorites()
