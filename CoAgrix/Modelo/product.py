from database import query_db, execute_db

# Columna de precio (en `publicaciones`) y valor de `tipo_precio` (en
# `historial_precios`) que le corresponde a cada rol comprador. Se usa para
# que el catálogo, los filtros/orden y el historial de precios muestren
# siempre el precio que el campesino definió para ese tipo de comprador.
PRICE_FIELD_BY_ROLE = {'Empresa': 'precio_empresa', 'Comerciante': 'precio_comerciante'}
PRICE_TYPE_BY_ROLE = {'Empresa': 'empresa', 'Comerciante': 'comerciante'}


def get_all_categories():
    return query_db("SELECT * FROM categorias ORDER BY nombre ASC")

def get_category_by_id(categoria_id):
    return query_db("SELECT * FROM categorias WHERE id = %s", (categoria_id,), one=True)

def get_all_products():
    return query_db("SELECT * FROM productos")

def get_or_create_producto(nombre, categoria_id, descripcion=None):
    """Busca un producto existente con el mismo nombre y categoría (para no
    llenar el catálogo de duplicados) y lo reutiliza; si no existe, lo crea.
    Devuelve el id del producto."""
    nombre = (nombre or '').strip()
    existing = query_db(
        "SELECT * FROM productos WHERE LOWER(nombre) = LOWER(%s) AND categoria_id = %s",
        (nombre, categoria_id), one=True
    )
    if existing:
        return existing['id']

    new_id = execute_db(
        "INSERT INTO productos (nombre, categoria_id, descripcion) VALUES (%s, %s, %s)",
        (nombre, categoria_id, descripcion)
    )
    return new_id

def get_active_publications(filters=None, page=None, per_page=12, price_field='precio_comerciante'):
    """Lista publicaciones activas aplicando filtros opcionales.

    Si se pasa `page`, pagina los resultados y devuelve una tupla
    (publicaciones, total_registros); total_registros sirve para calcular
    cuántas páginas hay en total. Si `page` es None, se mantiene el
    comportamiento original (devuelve solo la lista, sin paginar) para no
    romper otros lugares que ya llaman a esta función.

    `price_field` indica qué columna de precio ('precio_empresa' o
    'precio_comerciante') usar para el filtro de rango y el orden por
    precio; cada publicación siempre trae ambas columnas en el resultado.
    """
    if price_field not in ('precio_empresa', 'precio_comerciante'):
        price_field = 'precio_comerciante'
    base_query = """
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        JOIN categorias c ON pr.categoria_id = c.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        LEFT JOIN ubicaciones ub ON ca.ubicacion_id = ub.id
        WHERE p.estado = 'Activa'
    """
    args = []
    if filters:
        if filters.get('categoria'):
            base_query += " AND c.id = %s"
            args.append(filters['categoria'])
        if filters.get('municipio'):
            base_query += " AND ub.municipio LIKE %s"
            args.append(f"%{filters['municipio']}%")
        if filters.get('unidad'):
            base_query += " AND p.unidad_medida = %s"
            args.append(filters['unidad'])
        if filters.get('transporte') not in (None, ''):
            base_query += " AND p.transporte = %s"
            args.append(1 if str(filters['transporte']) in ('1', 'true', 'True') else 0)
        if filters.get('precio_min'):
            base_query += f" AND p.{price_field} >= %s"
            args.append(filters['precio_min'])
        if filters.get('precio_max'):
            base_query += f" AND p.{price_field} <= %s"
            args.append(filters['precio_max'])
        if filters.get('buscar'):
            base_query += " AND (pr.nombre LIKE %s OR p.titulo LIKE %s)"
            like = f"%{filters['buscar']}%"
            args.extend([like, like])

    select_query = (
        "SELECT p.*, pr.nombre as producto_nombre, c.nombre as categoria_nombre, "
        "u.nombre as campesino_nombre, ub.departamento, ub.municipio " + base_query
    )

    order_by = {
        'recientes': 'p.fecha_publicacion DESC',
        'antiguos': 'p.fecha_publicacion ASC',
        'precio_asc': f'p.{price_field} ASC',
        'precio_desc': f'p.{price_field} DESC',
    }.get((filters or {}).get('orden'), 'p.fecha_publicacion DESC')
    select_query += f" ORDER BY {order_by}"

    if page is None:
        return query_db(select_query, tuple(args))

    page = max(1, page)
    total_row = query_db("SELECT COUNT(*) as total " + base_query, tuple(args), one=True)
    total = total_row['total'] if total_row else 0

    select_query += " LIMIT %s OFFSET %s"
    items = query_db(select_query, tuple(args) + (per_page, (page - 1) * per_page))
    return items, total

def get_publication_by_id(publicacion_id):
    return query_db("""
        SELECT p.*, pr.nombre as producto_nombre, pr.categoria_id, c.nombre as categoria_nombre
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        JOIN categorias c ON pr.categoria_id = c.id
        WHERE p.id = %s
    """, (publicacion_id,), one=True)

def create_publication(campesino_id, producto_id, titulo, descripcion, precio_empresa,
                        precio_comerciante, cantidad, unidad, imagen=None, transporte=0):
    query = """
        INSERT INTO publicaciones
            (campesino_id, producto_id, titulo, descripcion, precio_empresa, precio_comerciante,
             cantidad_disponible, unidad_medida, imagen, transporte)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    publicacion_id = execute_db(query, (campesino_id, producto_id, titulo, descripcion,
                                         precio_empresa, precio_comerciante,
                                         cantidad, unidad, imagen, transporte))
    if publicacion_id:
        execute_db(
            "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo) "
            "VALUES (%s, 'empresa', %s, %s)",
            (publicacion_id, precio_empresa, precio_empresa)
        )
        execute_db(
            "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo) "
            "VALUES (%s, 'comerciante', %s, %s)",
            (publicacion_id, precio_comerciante, precio_comerciante)
        )
    return publicacion_id

def update_publication(publicacion_id, producto_id, titulo, descripcion, precio_empresa,
                        precio_comerciante, cantidad, unidad, transporte=0, imagen=None):

    actual = query_db("SELECT precio_empresa, precio_comerciante FROM publicaciones WHERE id = %s",
                       (publicacion_id,), one=True)

    if imagen:
        query = """
            UPDATE publicaciones
            SET producto_id = %s, titulo = %s, descripcion = %s, precio_empresa = %s,
                precio_comerciante = %s, cantidad_disponible = %s, unidad_medida = %s,
                transporte = %s, imagen = %s
            WHERE id = %s
        """
        args = (producto_id, titulo, descripcion, precio_empresa, precio_comerciante, cantidad,
                unidad, transporte, imagen, publicacion_id)
    else:
        query = """
            UPDATE publicaciones
            SET producto_id = %s, titulo = %s, descripcion = %s, precio_empresa = %s,
                precio_comerciante = %s, cantidad_disponible = %s, unidad_medida = %s,
                transporte = %s
            WHERE id = %s
        """
        args = (producto_id, titulo, descripcion, precio_empresa, precio_comerciante, cantidad,
                unidad, transporte, publicacion_id)

    result = execute_db(query, args)

    if result and actual is not None:
        for tipo_precio, anterior, nuevo in (
            ('empresa', actual['precio_empresa'], precio_empresa),
            ('comerciante', actual['precio_comerciante'], precio_comerciante),
        ):
            try:
                precio_anterior = float(anterior)
                precio_nuevo = float(nuevo)
            except (TypeError, ValueError):
                continue
            if precio_anterior != precio_nuevo:
                execute_db(
                    "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo) "
                    "VALUES (%s, %s, %s, %s)",
                    (publicacion_id, tipo_precio, precio_anterior, precio_nuevo)
                )

    if result:
        sync_publication_availability(publicacion_id)

    return result


def sync_publication_availability(publicacion_id):
    """Ajusta el estado de la publicación a la cantidad que tiene: una
    'Agotada' que recupera cantidad vuelve a 'Activa' (y a verse en el
    catálogo), y una 'Activa' sin cantidad pasa a 'Agotada'. Una publicación
    'Inactiva' (ocultada por un administrador) no se toca: el campesino no
    puede saltarse la moderación editándola."""
    execute_db(
        "UPDATE publicaciones SET estado = 'Activa' "
        "WHERE id = %s AND estado = 'Agotada' AND cantidad_disponible > 0",
        (publicacion_id,)
    )
    execute_db(
        "UPDATE publicaciones SET estado = 'Agotada' "
        "WHERE id = %s AND estado = 'Activa' AND cantidad_disponible <= 0",
        (publicacion_id,)
    )


def delete_publication(publicacion_id):
    return execute_db("DELETE FROM publicaciones WHERE id = %s", (publicacion_id,))


def decrease_stock(publicacion_id, cantidad):
    """Descuenta cantidad disponible tras un pedido; si llega a 0, marca la
    publicación como Agotada."""
    execute_db(
        "UPDATE publicaciones SET cantidad_disponible = GREATEST(cantidad_disponible - %s, 0) WHERE id = %s",
        (cantidad, publicacion_id)
    )
    execute_db(
        "UPDATE publicaciones SET estado = 'Agotada' WHERE id = %s AND cantidad_disponible <= 0",
        (publicacion_id,)
    )


def insert_archivo(publicacion_id, ruta):
    """Registra en `archivos` la relación publicacion_id -> ruta de imagen.
    Se usa junto con el campo `imagen` de `publicaciones` para dejar
    también la relación explícita en `archivos`, tal como puede
    necesitarla la vista de detalle (galería)."""
    return execute_db(
        "INSERT INTO archivos (publicacion_id, ruta) VALUES (%s, %s)",
        (publicacion_id, ruta)
    )


def get_archivos_by_publicacion(publicacion_id):
    return query_db(
        "SELECT * FROM archivos WHERE publicacion_id = %s ORDER BY id ASC",
        (publicacion_id,)
    )


def delete_archivos_by_publicacion(publicacion_id):
    """Elimina todas las filas de `archivos` asociadas a una publicación.
    Se usa al reemplazar la imagen principal (para no dejar apuntando a
    un archivo que ya no existe) o antes de borrar la publicación."""
    return execute_db(
        "DELETE FROM archivos WHERE publicacion_id = %s",
        (publicacion_id,)
    )


def get_price_history(publicacion_id):
    """Historial de precios de UNA publicación específica, en orden cronológico."""
    return query_db("""
        SELECT * FROM historial_precios
        WHERE publicacion_id = %s
        ORDER BY fecha_cambio ASC
    """, (publicacion_id,))


def get_price_comparison(price_field, buscar=None):
    """Precio mínimo, máximo y número de vendedores por producto, entre las
    publicaciones activas. `price_field` es la columna de precio del rol
    ('precio_empresa' o 'precio_comerciante'). Si se pasa `buscar`, solo
    trae los productos cuyo nombre lo contiene."""
    if price_field not in ('precio_empresa', 'precio_comerciante'):
        price_field = 'precio_comerciante'
    query = f"""
        SELECT pr.id AS producto_id, pr.nombre,
               MIN(p.{price_field}) AS precio_min, MAX(p.{price_field}) AS precio_max,
               COUNT(DISTINCT p.campesino_id) AS num_vendedores
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        WHERE p.estado = 'Activa'
    """
    params = []
    if buscar:
        # Se escapan % y _ (con '!') para que se busquen tal cual, no como comodines.
        term = buscar.replace('!', '!!').replace('%', '!%').replace('_', '!_')
        query += " AND pr.nombre LIKE %s ESCAPE '!'"
        params.append(f"%{term}%")
    query += " GROUP BY pr.id, pr.nombre ORDER BY pr.nombre ASC"
    return query_db(query, tuple(params)) or []


def get_products_with_history():
    """Lista de productos (nombre genérico) que tienen al menos una
    publicación activa, para que el comerciante elija cuál comparar."""
    return query_db("""
        SELECT DISTINCT pr.id, pr.nombre
        FROM productos pr
        JOIN publicaciones p ON p.producto_id = pr.id
        WHERE p.estado = 'Activa'
        ORDER BY pr.nombre ASC
    """)


def get_price_history_by_product(producto_id, tipo_precio='comerciante'):
    """Historial de precios de TODAS las publicaciones de un mismo producto
    (across distintos vendedores), para comparar cómo ha variado el precio
    entre campesinos. Cada fila trae quién es el vendedor y en qué
    publicación ocurrió el cambio.

    `tipo_precio` ('empresa' o 'comerciante') filtra el historial al tipo de
    precio que le corresponde a quien está comparando."""
    if tipo_precio not in ('empresa', 'comerciante'):
        tipo_precio = 'comerciante'
    return query_db("""
        SELECT h.*, p.titulo, p.campesino_id, u.nombre as campesino_nombre
        FROM historial_precios h
        JOIN publicaciones p ON h.publicacion_id = p.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        WHERE p.producto_id = %s AND h.tipo_precio = %s
        ORDER BY h.fecha_cambio ASC
    """, (producto_id, tipo_precio))
