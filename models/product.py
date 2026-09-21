from database import query_db, execute_db

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

def get_active_publications(filters=None, page=None, per_page=12):
    """Lista publicaciones activas aplicando filtros opcionales.

    Si se pasa `page`, pagina los resultados y devuelve una tupla
    (publicaciones, total_registros); total_registros sirve para calcular
    cuántas páginas hay en total. Si `page` es None, se mantiene el
    comportamiento original (devuelve solo la lista, sin paginar) para no
    romper otros lugares que ya llaman a esta función.
    """
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
            base_query += " AND p.precio >= %s"
            args.append(filters['precio_min'])
        if filters.get('precio_max'):
            base_query += " AND p.precio <= %s"
            args.append(filters['precio_max'])
        if filters.get('buscar'):
            base_query += " AND (pr.nombre LIKE %s OR p.titulo LIKE %s)"
            like = f"%{filters['buscar']}%"
            args.extend([like, like])

    select_query = (
        "SELECT p.*, pr.nombre as producto_nombre, c.nombre as categoria_nombre, "
        "u.nombre as campesino_nombre, ub.departamento, ub.municipio " + base_query
    )
    select_query += " ORDER BY p.fecha_publicacion DESC"

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

def create_publication(campesino_id, producto_id, titulo, descripcion, precio, cantidad, unidad,
                        imagen=None, transporte=0):
    query = """
        INSERT INTO publicaciones
            (campesino_id, producto_id, titulo, descripcion, precio, cantidad_disponible,
             unidad_medida, imagen, transporte)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    publicacion_id = execute_db(query, (campesino_id, producto_id, titulo, descripcion, precio,
                                         cantidad, unidad, imagen, transporte))
    if publicacion_id:
        # Deja el primer registro en el historial de precios, con el precio
        # inicial de publicación como punto de partida.
        execute_db(
            "INSERT INTO historial_precios (publicacion_id, precio_anterior, precio_nuevo) "
            "VALUES (%s, %s, %s)",
            (publicacion_id, precio, precio)
        )
    return publicacion_id

def update_publication(publicacion_id, producto_id, titulo, descripcion, precio, cantidad, unidad,
                        transporte=0, imagen=None):
    # Antes de actualizar, revisamos si el precio realmente cambió para
    # dejar constancia en el historial de precios.
    actual = query_db("SELECT precio FROM publicaciones WHERE id = %s", (publicacion_id,), one=True)

    if imagen:
        query = """
            UPDATE publicaciones
            SET producto_id = %s, titulo = %s, descripcion = %s, precio = %s,
                cantidad_disponible = %s, unidad_medida = %s, transporte = %s, imagen = %s
            WHERE id = %s
        """
        args = (producto_id, titulo, descripcion, precio, cantidad, unidad, transporte, imagen,
                publicacion_id)
    else:
        query = """
            UPDATE publicaciones
            SET producto_id = %s, titulo = %s, descripcion = %s, precio = %s,
                cantidad_disponible = %s, unidad_medida = %s, transporte = %s
            WHERE id = %s
        """
        args = (producto_id, titulo, descripcion, precio, cantidad, unidad, transporte,
                publicacion_id)

    result = execute_db(query, args)

    if result and actual is not None:
        try:
            precio_anterior = float(actual['precio'])
            precio_nuevo = float(precio)
        except (TypeError, ValueError):
            precio_anterior = precio_nuevo = None

        if precio_anterior is not None and precio_anterior != precio_nuevo:
            execute_db(
                "INSERT INTO historial_precios (publicacion_id, precio_anterior, precio_nuevo) "
                "VALUES (%s, %s, %s)",
                (publicacion_id, precio_anterior, precio_nuevo)
            )

    return result

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


def get_price_history(publicacion_id):
    """Historial de precios de UNA publicación específica, en orden cronológico."""
    return query_db("""
        SELECT * FROM historial_precios
        WHERE publicacion_id = %s
        ORDER BY fecha_cambio ASC
    """, (publicacion_id,))


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


def get_price_history_by_product(producto_id):
    """Historial de precios de TODAS las publicaciones de un mismo producto
    (across distintos vendedores), para comparar cómo ha variado el precio
    entre campesinos. Cada fila trae quién es el vendedor y en qué
    publicación ocurrió el cambio."""
    return query_db("""
        SELECT h.*, p.titulo, p.campesino_id, u.nombre as campesino_nombre
        FROM historial_precios h
        JOIN publicaciones p ON h.publicacion_id = p.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        WHERE p.producto_id = %s
        ORDER BY h.fecha_cambio ASC
    """, (producto_id,))
