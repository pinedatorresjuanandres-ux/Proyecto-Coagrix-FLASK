import os
import uuid
from flask import render_template, request, redirect, url_for, session, flash
from PIL import Image, UnidentifiedImageError
from models.user import get_farmer_data
from models.product import (
    create_publication, get_all_products, get_all_categories,
    get_or_create_producto, get_publication_by_id, update_publication,
    delete_publication
)
from config import Config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
# Formatos que Pillow debe reconocer realmente dentro del archivo; evita que
# alguien suba un .php o .html renombrado a "foto.png" (la extensión sola
# no dice nada sobre el contenido real del archivo).
ALLOWED_PIL_FORMATS = {'PNG', 'JPEG', 'WEBP', 'GIF'}
MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8MB por imagen


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
            img.verify()  # valida integridad sin cargar toda la imagen en memoria
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as img:
            fmt = (img.format or '').upper()
        file_storage.stream.seek(0)
        return fmt in ALLOWED_PIL_FORMATS
    except (UnidentifiedImageError, OSError, ValueError):
        return False


def _save_image(file):
    """Guarda la imagen subida con un nombre único y devuelve la ruta relativa
    (dentro de /static) para guardarla en la base de datos. Si no se sube
    ninguna imagen válida, devuelve None (se mostrará la imagen por defecto).
    Valida tanto la extensión como el contenido real del archivo."""
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
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    return f"uploads/{filename}"


def _read_product_form(form):
    return {
        'nombre_producto': (form.get('nombre_producto') or '').strip(),
        'categoria_id': form.get('categoria_id'),
        'descripcion': form.get('descripcion'),
        'precio': form.get('precio'),
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

        producto_id = get_or_create_producto(
            data['nombre_producto'], data['categoria_id'], data['descripcion']
        )

        imagen = _save_image(request.files.get('imagen'))

        success = create_publication(
            campesino['id'], producto_id, data['nombre_producto'], data['descripcion'],
            data['precio'], data['cantidad'], data['unidad'],
            imagen=imagen, transporte=data['transporte']
        )
        if success:
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

        producto_id = get_or_create_producto(
            data['nombre_producto'], data['categoria_id'], data['descripcion']
        )
        imagen = _save_image(request.files.get('imagen'))

        update_publication(
            publicacion_id, producto_id, data['nombre_producto'], data['descripcion'],
            data['precio'], data['cantidad'], data['unidad'],
            transporte=data['transporte'], imagen=imagen
        )
        flash('Publicación actualizada exitosamente.', 'success')
        return redirect(url_for('farmer.publications'))

    categories = get_all_categories()
    return render_template('editar_publicacion.html', publication=pub, categories=categories)


def delete_pub(publicacion_id):
    campesino = get_farmer_data(session['user_id'])
    pub = get_publication_by_id(publicacion_id)

    if pub and campesino and pub['campesino_id'] == campesino['id']:
        delete_publication(publicacion_id)
        flash('Publicación eliminada correctamente.', 'success')
    else:
        flash('No tienes permiso para eliminar esta publicación.', 'error')

    return redirect(url_for('farmer.publications'))
