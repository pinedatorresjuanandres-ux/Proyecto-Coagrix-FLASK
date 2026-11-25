from database import query_db, execute_db
from Modelo.order import ESTADOS_PEDIDO

def get_farmer_profile(usuario_id):
    return query_db("""
        SELECT c.*, u.nombre, u.email, ub.departamento, ub.municipio, ub.direccion
        FROM campesinos c
        JOIN usuarios u ON c.usuario_id = u.id
        LEFT JOIN ubicaciones ub ON c.ubicacion_id = ub.id
        WHERE c.usuario_id = %s
    """, (usuario_id,), one=True)

def update_farmer_profile(usuario_id, telefono, descripcion, ubicacion_id):
    query = """
        UPDATE campesinos 
        SET telefono = %s, descripcion = %s, ubicacion_id = %s
        WHERE usuario_id = %s
    """
    return execute_db(query, (telefono, descripcion, ubicacion_id, usuario_id))

def get_farmer_crops(campesino_id):
    return query_db("SELECT * FROM cultivos WHERE campesino_id = %s", (campesino_id,))

def create_crop(campesino_id, nombre, area, fecha_siembra, estado):
    query = "INSERT INTO cultivos (campesino_id, nombre, area, fecha_siembra, estado) VALUES (%s, %s, %s, %s, %s)"
    return execute_db(query, (campesino_id, nombre, area, fecha_siembra, estado))

def get_farmer_publications(campesino_id, filters=None):
    """Publicaciones del campesino con filtros de gestión.

    A diferencia del catálogo, aquí sí se muestran inactivas y agotadas: el
    productor necesita administrarlas aunque no estén a la venta.
    """
    filters = filters or {}
    query = """
        SELECT p.*, pr.nombre as producto_nombre, c.nombre as categoria_nombre
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        JOIN categorias c ON pr.categoria_id = c.id
        WHERE p.campesino_id = %s
    """
    params = [campesino_id]
    if filters.get('buscar'):
        query += " AND (p.titulo LIKE %s OR pr.nombre LIKE %s)"
        term = f"%{filters['buscar']}%"
        params.extend([term, term])
    if filters.get('categoria'):
        query += " AND c.id = %s"
        params.append(filters['categoria'])
    if filters.get('estado') in ('Activa', 'Inactiva', 'Agotada'):
        query += " AND p.estado = %s"
        params.append(filters['estado'])
    query += " ORDER BY p.fecha_publicacion DESC"
    return query_db(query, tuple(params))

def _parse_productos_pedido(raw):
    """Convierte el string armado por GROUP_CONCAT/CONCAT_WS (formato
    'titulo|imagen|cantidad|unidad;;titulo|imagen|cantidad|unidad;;...')
    en una lista de dicts lista para usar en la plantilla."""
    if not raw:
        return []
    items = []
    for chunk in raw.split(';;'):
        partes = chunk.split('|')
        if len(partes) != 4:
            continue
        titulo, imagen, cantidad, unidad = partes
        try:
            cantidad = float(cantidad)
            if cantidad == int(cantidad):
                cantidad = int(cantidad)
        except (TypeError, ValueError):
            pass
        items.append({
            'titulo': titulo,
            'imagen': imagen or None,
            'cantidad': cantidad,
            'unidad_medida': unidad,
        })
    return items


def get_farmer_orders(campesino_id, filters=None):
    """Pedidos que incluyen productos del campesino.

    ``productos_detalle`` se agrega deliberadamente a la lista (con
    imagen y cantidad por producto): evita que el campesino tenga que
    abrir cada pedido para saber qué y cuánto le solicitaron.
    """
    filters = filters or {}
    query = """
        SELECT p.*, u.nombre as comprador_nombre, u.email,
               GROUP_CONCAT(DISTINCT CONCAT_WS('|', pub.titulo, IFNULL(pub.imagen, ''), dp.cantidad, pub.unidad_medida)
                            ORDER BY pub.titulo SEPARATOR ';;') AS productos_raw
        FROM pedidos p
        JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        JOIN publicaciones pub ON dp.publicacion_id = pub.id
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE pub.campesino_id = %s
    """
    params = [campesino_id]
    if filters.get('estado') in ESTADOS_PEDIDO:
        query += " AND p.estado = %s"
        params.append(filters['estado'])
    if filters.get('comprador'):
        query += " AND (u.nombre LIKE %s OR u.email LIKE %s)"
        term = f"%{filters['comprador']}%"
        params.extend([term, term])
    # Por orden de llegada, el más reciente primero. Se ordena por `id` (crece
    # con cada pedido) y no por `fecha_pedido`: una fecha mal cargada o dos
    # pedidos en el mismo segundo dejaban la lista desordenada.
    query += " GROUP BY p.id, u.nombre, u.email ORDER BY p.id DESC"
    orders = query_db(query, tuple(params)) or []
    for order in orders:
        order['productos_detalle'] = _parse_productos_pedido(order.pop('productos_raw', None))
    return orders

def get_farmer_sales_stats(campesino_id):
    stats = query_db("""
        SELECT 
            COUNT(DISTINCT CASE WHEN p.estado = 'Completado' THEN p.id END) as total_pedidos,
            COALESCE(SUM(CASE WHEN p.estado = 'Completado'
                              THEN dp.cantidad * dp.precio_unitario ELSE 0 END), 0) as ingresos_totales,
            COUNT(DISTINCT pub.id) as total_publicaciones
        FROM publicaciones pub
        LEFT JOIN detalle_pedidos dp ON pub.id = dp.publicacion_id
        LEFT JOIN pedidos p ON dp.pedido_id = p.id
        WHERE pub.campesino_id = %s
    """, (campesino_id,), one=True)
    return stats if stats else {'total_pedidos': 0, 'ingresos_totales': 0, 'total_publicaciones': 0}

def get_farmer_monthly_product_sales(campesino_id, desde, hasta):
    """Ventas por producto del campesino en un mes: cuánto se vendió y cuánto
    ganó. `desde` (inclusive) y `hasta` (exclusivo) son las fechas
    'YYYY-MM-DD' que delimitan el mes. Solo cuentan los pedidos Completados,
    igual que los ingresos del panel; los pendientes, rechazados y cancelados
    no son ventas."""
    return query_db("""
        SELECT pub.id, pub.titulo, pub.unidad_medida,
               SUM(dp.cantidad) AS cantidad_vendida,
               SUM(dp.cantidad * dp.precio_unitario) AS ganancia
        FROM detalle_pedidos dp
        JOIN pedidos p ON p.id = dp.pedido_id
        JOIN publicaciones pub ON pub.id = dp.publicacion_id
        WHERE pub.campesino_id = %s AND p.estado = 'Completado'
          AND p.fecha_pedido >= %s AND p.fecha_pedido < %s
        GROUP BY pub.id, pub.titulo, pub.unidad_medida
        ORDER BY ganancia DESC, pub.titulo ASC
    """, (campesino_id, desde, hasta)) or []

def get_farmer_income_history(campesino_id):
    """Ingresos mensuales (pedidos completados) de los últimos 12 meses,
    para graficar la evolución de ventas del campesino."""
    return query_db("""
        SELECT DATE_FORMAT(p.fecha_pedido, '%%Y-%%m') AS mes,
               SUM(dp.cantidad * dp.precio_unitario) AS ingresos
        FROM detalle_pedidos dp
        JOIN publicaciones pub ON dp.publicacion_id = pub.id
        JOIN pedidos p ON dp.pedido_id = p.id
        WHERE pub.campesino_id = %s AND p.estado = 'Completado'
          AND p.fecha_pedido >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY mes
        ORDER BY mes
    """, (campesino_id,)) or []
