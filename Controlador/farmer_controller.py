import os
import re
from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.utils import secure_filename

from Modelo.user import get_farmer_data, update_user_profile, get_user_by_email, create_location, update_location
from Modelo.farmer import get_farmer_profile, get_farmer_publications, get_farmer_orders, get_farmer_sales_stats, get_farmer_income_history, get_farmer_monthly_product_sales, update_farmer_profile
from Modelo.product import (
    create_publication, get_all_products, get_all_categories,
    get_or_create_producto, get_publication_by_id, update_publication,
    delete_publication, insert_archivo, delete_archivos_by_publicacion,
    get_products_with_history, get_price_history_by_product, get_price_comparison
)
from database import query_db
from Modelo.order import get_order, update_order_status, get_order_details, order_belongs_to_farmer, release_order
from config import Config

farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_PIL_FORMATS = {'PNG', 'JPEG', 'WEBP', 'GIF'}
MAX_IMAGE_BYTES = 8 * 1024 * 1024

MAX_IMAGE_DIMENSION = 1600  
IMAGE_QUALITY = 85


@farmer_bp.before_request
def check_farmer():
    if 'user_id' not in session or session.get('role_name') != 'Campesino':
        return redirect(url_for('auth.login_page'))


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _is_genuine_image(file_storage):
    """Verifica que el contenido del archivo sea realmente una imagen
    válida (no solo que el nombre termine en .png/.jpg). Usa Pillow para
    abrir y decodificar el archivo; si falla o el formato detectado no es
    uno de los permitidos, se rechaza."""
    try:
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as img:
            img.verify()
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as img:
            fmt = (img.format or '').upper()
        file_storage.stream.seek(0)
        return fmt in ALLOWED_PIL_FORMATS
    except (UnidentifiedImageError, OSError, ValueError):
        return False


def _save_image(file):
    """Guarda la imagen subida conservando el nombre original del
    archivo (sanitizado), validada y optimizada. Si ya existe un
    archivo con ese nombre, le agrega un sufijo numérico para no
    sobrescribirlo. Devuelve la ruta relativa o None si no hay imagen
    válida."""
    if not file or file.filename == '':
        return None
    if not _allowed_file(file.filename):
        flash('Formato de imagen no permitido. Usa PNG, JPG, JPEG, WEBP o GIF.', 'error')
        return None

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > MAX_IMAGE_BYTES:
        flash('La imagen supera el tamaño máximo permitido (8MB).', 'error')
        return None

    if not _is_genuine_image(file):
        flash('El archivo no parece ser una imagen válida.', 'error')
        return None

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[1].lower()
    base_name = secure_filename(file.filename.rsplit('.', 1)[0]) or 'imagen'
    filename = f"{base_name}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    # Si ya existe un archivo con ese nombre (otra publicación subió una
    # imagen con el mismo nombre original), se le agrega un sufijo
    # numérico para no sobrescribirla, conservando el nombre que el
    # campesino le puso.
    counter = 1
    while os.path.exists(filepath):
        filename = f"{base_name}_{counter}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        counter += 1

    if not _save_processed_image(file, filepath, ext):
        file.stream.seek(0)
        file.save(filepath)

    return f"uploads/{filename}"


def _save_processed_image(file, filepath, ext):
    """Corrige orientación EXIF, redimensiona proporcionalmente si excede
    MAX_IMAGE_DIMENSION y guarda optimizada. True si se guardó bien."""
    try:
        file.stream.seek(0)
        with Image.open(file.stream) as img:
            if getattr(img, 'is_animated', False):
                file.stream.seek(0)
                file.save(filepath)
                return True

            img = ImageOps.exif_transpose(img)

            if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)

            save_kwargs = {'optimize': True}
            if ext in ('jpg', 'jpeg'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    fondo = Image.new('RGB', img.size, (255, 255, 255))
                    img = img.convert('RGBA')
                    fondo.paste(img, mask=img.split()[-1])
                    img = fondo
                else:
                    img = img.convert('RGB')
                save_kwargs.update(format='JPEG', quality=IMAGE_QUALITY, progressive=True)
            elif ext == 'webp':
                save_kwargs.update(format='WEBP', quality=IMAGE_QUALITY)
            elif ext == 'png':
                save_kwargs.update(format='PNG')
            elif ext == 'gif':
                save_kwargs.update(format='GIF')

            img.save(filepath, **save_kwargs)
        return True
    except Exception:
        return False


def _delete_physical_image(ruta):
    """Borra físicamente el archivo de static/uploads/ que corresponde a
    una imagen anterior (al reemplazarla o al eliminar la publicación).

    Es defensivo a propósito: solo borra rutas que empiecen literalmente
    con 'uploads/' y cuyo nombre de archivo, una vez resuelto, siga
    quedando dentro de Config.UPLOAD_FOLDER (evita borrar archivos fuera
    de esa carpeta si 'ruta' llegara a contener algo como '../../').
    Nunca borra la imagen por defecto ni falla si el archivo ya no existe.
    """
    if not ruta or not ruta.startswith('uploads/'):
        return
    filename = os.path.basename(ruta)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    if os.path.commonpath([os.path.abspath(filepath), Config.UPLOAD_FOLDER]) != Config.UPLOAD_FOLDER:
        return
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
    except OSError:
        pass


def _read_product_form(form):
    return {
        'nombre_producto': (form.get('nombre_producto') or '').strip(),
        'categoria_id': form.get('categoria_id'),
        'descripcion': form.get('descripcion'),
        'precio_empresa': form.get('precio_empresa'),
        'precio_comerciante': form.get('precio_comerciante'),
        'cantidad': form.get('cantidad'),
        'unidad': form.get('unidad'),
        'transporte': 1 if form.get('transporte') else 0,
    }


def create_pub():
    if request.method == 'POST':
        campesino = get_farmer_data(session['user_id'])
        if not campesino:
            flash('Tu perfil de campesino no está configurado. Contacta al administrador.', 'error')
            return redirect(url_for('farmer.dashboard'))

        data = _read_product_form(request.form)

        if not data['nombre_producto'] or not data['categoria_id']:
            flash('El nombre del producto y la categoría son obligatorios.', 'error')
            categories = get_all_categories()
            return render_template('crear_publicacion.html', categories=categories, form=data)

        if not data['precio_empresa'] or not data['precio_comerciante']:
            flash('Ingresa el precio para empresa y el precio para comerciante.', 'error')
            categories = get_all_categories()
            return render_template('crear_publicacion.html', categories=categories, form=data)

        producto_id = get_or_create_producto(
            data['nombre_producto'], data['categoria_id'], data['descripcion']
        )

        imagen = _save_image(request.files.get('imagen'))

        success = create_publication(
            campesino['id'], producto_id, data['nombre_producto'], data['descripcion'],
            data['precio_empresa'], data['precio_comerciante'], data['cantidad'], data['unidad'],
            imagen=imagen, transporte=data['transporte']
        )
        if success:
            if imagen:

                insert_archivo(success, imagen)
            flash('Producto publicado exitosamente. Ya está visible en el catálogo.', 'success')
            return redirect(url_for('farmer.publications'))
        else:
            flash('Error al crear la publicación.', 'error')

    categories = get_all_categories()
    return render_template('crear_publicacion.html', categories=categories, form=None)


def edit_pub(publicacion_id):
    campesino = get_farmer_data(session['user_id'])
    pub = get_publication_by_id(publicacion_id)

    if not pub or not campesino or pub['campesino_id'] != campesino['id']:
        flash('No tienes permiso para editar esta publicación.', 'error')
        return redirect(url_for('farmer.publications'))

    if request.method == 'POST':
        data = _read_product_form(request.form)

        if not data['nombre_producto'] or not data['categoria_id']:
            flash('El nombre del producto y la categoría son obligatorios.', 'error')
            categories = get_all_categories()
            return render_template('editar_publicacion.html', publication=pub, categories=categories)

        if not data['precio_empresa'] or not data['precio_comerciante']:
            flash('Ingresa el precio para empresa y el precio para comerciante.', 'error')
            categories = get_all_categories()
            return render_template('editar_publicacion.html', publication=pub, categories=categories)

        producto_id = get_or_create_producto(
            data['nombre_producto'], data['categoria_id'], data['descripcion']
        )
        imagen_anterior = pub.get('imagen')
        imagen = _save_image(request.files.get('imagen'))

        update_publication(
            publicacion_id, producto_id, data['nombre_producto'], data['descripcion'],
            data['precio_empresa'], data['precio_comerciante'], data['cantidad'], data['unidad'],
            transporte=data['transporte'], imagen=imagen
        )

        if imagen:

            delete_archivos_by_publicacion(publicacion_id)
            insert_archivo(publicacion_id, imagen)
            if imagen_anterior and imagen_anterior != imagen:
                _delete_physical_image(imagen_anterior)

        actualizada = get_publication_by_id(publicacion_id)
        if pub['estado'] == 'Agotada' and actualizada and actualizada['estado'] == 'Activa':
            flash('Publicación actualizada. Tu producto volvió a estar disponible en el catálogo.', 'success')
        else:
            flash('Publicación actualizada exitosamente.', 'success')
        return redirect(url_for('farmer.publications'))

    categories = get_all_categories()
    return render_template('editar_publicacion.html', publication=pub, categories=categories)


def delete_pub(publicacion_id):
    campesino = get_farmer_data(session['user_id'])
    pub = get_publication_by_id(publicacion_id)

    if pub and campesino and pub['campesino_id'] == campesino['id']:
        imagen = pub.get('imagen')
        delete_publication(publicacion_id)
        _delete_physical_image(imagen)
        flash('Publicación eliminada correctamente.', 'success')
    else:
        flash('No tienes permiso para eliminar esta publicación.', 'error')

    return redirect(url_for('farmer.publications'))


def _require_own_order(pedido_id):
    """Devuelve el registro del campesino si el pedido le pertenece
    (contiene al menos una de sus publicaciones); si no, aborta con 403.
    Centraliza el chequeo de propiedad para las rutas de pedidos de abajo,
    en vez de repetirlo en cada una."""
    farmer = get_farmer_data(session['user_id'])
    if not farmer or not order_belongs_to_farmer(pedido_id, farmer['id']):
        abort(403)
    return farmer


@farmer_bp.route('/dashboard')
def dashboard():
    farmer = get_farmer_data(session['user_id'])
    stats = get_farmer_sales_stats(farmer['id']) if farmer else None
    income_history = get_farmer_income_history(farmer['id']) if farmer else []
    return render_template('farmer/dashboard.html', farmer=farmer, stats=stats, income_history=income_history)


MESES = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
         'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre')


def _month_start(year, month):
    """Primer día del mes, normalizando desbordes (mes 0 -> diciembre del año anterior)."""
    year += (month - 1) // 12
    return date(year, (month - 1) % 12 + 1, 1)


@farmer_bp.route('/estadisticas')
def stats_route():
    """Ventas del mes por producto: cantidad vendida y ganancia. El mes llega
    como ?mes=AAAA-MM; si falta o no es válido se usa el mes actual."""
    hoy = date.today()
    match = re.fullmatch(r'(\d{4})-(0[1-9]|1[0-2])', request.args.get('mes', ''))
    year, month = (int(match.group(1)), int(match.group(2))) if match else (hoy.year, hoy.month)
    if not 2000 <= year <= 2100:
        year, month = hoy.year, hoy.month

    inicio = _month_start(year, month)
    fin = _month_start(year, month + 1)

    farmer = get_farmer_data(session['user_id'])
    rows = get_farmer_monthly_product_sales(farmer['id'], inicio.isoformat(), fin.isoformat()) if farmer else []
    total = sum(float(r['ganancia'] or 0) for r in rows)

    # Selector: los últimos 12 meses (más el elegido si queda fuera de ese rango).
    opciones = [_month_start(hoy.year, hoy.month - i) for i in range(12)]
    if inicio not in opciones:
        opciones.append(inicio)
        opciones.sort(reverse=True)
    meses = [{'valor': d.strftime('%Y-%m'), 'nombre': f'{MESES[d.month - 1]} {d.year}'} for d in opciones]

    return render_template('farmer/statistics.html', rows=rows, total=total, meses=meses,
                           mes_actual=inicio.strftime('%Y-%m'),
                           mes_nombre=f'{MESES[inicio.month - 1]} {inicio.year}')


@farmer_bp.route('/comparar')
def compare_route():
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

    return render_template('farmer/compare.html',
                         price_comparison=price_comparison,
                         buscar=buscar,
                         productos=productos,
                         historial=historial,
                         producto_seleccionado=producto_seleccionado,
                         producto_id=producto_id)


@farmer_bp.route('/perfil', methods=['GET', 'POST'])
def profile():
    farmer = get_farmer_profile(session['user_id'])
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        existing = get_user_by_email(email)
        if not nombre or not email or (existing and existing['id'] != session['user_id']):
            flash('Ingresa un nombre y un correo disponible.', 'error')
            return redirect(url_for('farmer.profile'))
        telefono = request.form.get('telefono')
        descripcion = request.form.get('descripcion')
        departamento = (request.form.get('departamento') or '').strip()
        municipio = (request.form.get('municipio') or '').strip()

        ubicacion_id = farmer['ubicacion_id'] if farmer else None
        if departamento and municipio:
            if ubicacion_id:
                update_location(ubicacion_id, departamento, municipio)
            else:
                ubicacion_id = create_location(departamento, municipio)

        update_farmer_profile(session['user_id'], telefono, descripcion, ubicacion_id)
        update_user_profile(session['user_id'], nombre, email)
        session['user_name'] = nombre
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('farmer.profile'))
    return render_template('farmer/profile.html', farmer=farmer)


@farmer_bp.route('/publicaciones')
def publications():
    farmer = get_farmer_data(session['user_id'])
    filters = {key: request.args.get(key) for key in ('buscar', 'categoria', 'estado') if request.args.get(key)}
    pubs = get_farmer_publications(farmer['id'], filters) if farmer else []
    return render_template('farmer/publications.html', publications=pubs,
                           categories=get_all_categories(), filters=filters)


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
    filters = {key: request.args.get(key) for key in ('estado', 'comprador') if request.args.get(key)}
    orders = get_farmer_orders(farmer['id'], filters) if farmer else []
    return render_template('farmer/orders.html', orders=orders, filters=filters)


@farmer_bp.route('/pedidos/<int:pedido_id>')
def order_detail_route(pedido_id):
    _require_own_order(pedido_id)
    details = get_order_details(pedido_id)
    order = get_order(pedido_id)
    return render_template('farmer/order_detail.html', details=details, order=order)


@farmer_bp.route('/pedidos/<int:pedido_id>/aceptar', methods=['POST'])
def accept_order_route(pedido_id):
    _require_own_order(pedido_id)
    if (get_order(pedido_id) or {}).get('estado') != 'Pendiente':
        flash('Este pedido ya no está pendiente (pudo ser cancelado por el comprador).', 'error')
        return redirect(url_for('farmer.orders_route'))
    update_order_status(pedido_id, 'Aceptado')
    flash('Pedido aceptado.', 'success')
    return redirect(url_for('farmer.orders_route'))


@farmer_bp.route('/pedidos/<int:pedido_id>/rechazar', methods=['POST'])
def reject_order_route(pedido_id):
    _require_own_order(pedido_id)
    # Rechazar también devuelve al inventario lo que el pedido había descontado.
    if release_order(pedido_id, 'Rechazado', ('Pendiente',)):
        flash('Pedido rechazado.', 'success')
    else:
        flash('Este pedido ya no está pendiente (pudo ser cancelado por el comprador).', 'error')
    return redirect(url_for('farmer.orders_route'))


@farmer_bp.route('/pedidos/<int:pedido_id>/completar', methods=['POST'])
def complete_order_route(pedido_id):
    _require_own_order(pedido_id)
    if (get_order(pedido_id) or {}).get('estado') != 'Aceptado':
        flash('Solo se pueden completar pedidos aceptados (pudo ser cancelado por el comprador).', 'error')
        return redirect(url_for('farmer.orders_route'))
    update_order_status(pedido_id, 'Completado')
    flash('Pedido marcado como completado.', 'success')
    return redirect(url_for('farmer.orders_route'))
