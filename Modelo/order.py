from mysql.connector import Error

from database import query_db, execute_db, get_db_connection

ESTADOS_PEDIDO = ('Pendiente', 'Aceptado', 'Rechazado', 'Completado', 'Cancelado')

# Estados desde los que el comprador todavía puede cancelar su pedido.
ESTADOS_CANCELABLES = ('Pendiente', 'Aceptado')

def create_order(usuario_id, total=None):
    query = "INSERT INTO pedidos (usuario_id, estado, total) VALUES (%s, 'Pendiente', %s)"
    return execute_db(query, (usuario_id, total))

def add_order_detail(pedido_id, publicacion_id, cantidad, precio_unitario):
    query = "INSERT INTO detalle_pedidos (pedido_id, publicacion_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
    return execute_db(query, (pedido_id, publicacion_id, cantidad, precio_unitario))

def get_order(pedido_id):
    return query_db("SELECT * FROM pedidos WHERE id = %s", (pedido_id,), one=True)


def get_order_for_buyer(pedido_id, usuario_id):
    """Devuelve el pedido solo si pertenece al comprador dado; en caso
    contrario devuelve None. Evita que un usuario vea/opere pedidos ajenos
    adivinando el id en la URL (IDOR)."""
    return query_db(
        "SELECT * FROM pedidos WHERE id = %s AND usuario_id = %s",
        (pedido_id, usuario_id), one=True
    )


def order_belongs_to_farmer(pedido_id, campesino_id):
    """True si el pedido contiene al menos una publicación del campesino
    dado, es decir, si el campesino tiene permiso para ver/gestionar ese
    pedido. Evita que un campesino vea o cambie el estado de pedidos que
    no le pertenecen."""
    result = query_db("""
        SELECT 1
        FROM detalle_pedidos dp
        JOIN publicaciones pub ON dp.publicacion_id = pub.id
        WHERE dp.pedido_id = %s AND pub.campesino_id = %s
        LIMIT 1
    """, (pedido_id, campesino_id), one=True)
    return result is not None

def update_order_status(pedido_id, estado):
    query = "UPDATE pedidos SET estado = %s WHERE id = %s"
    return execute_db(query, (estado, pedido_id))

def release_order(pedido_id, nuevo_estado, estados_permitidos, usuario_id=None):
    """Cancela o rechaza un pedido y devuelve a cada publicación la cantidad
    que el pedido había descontado, todo en una sola transacción (o se hace
    todo o no se hace nada). Es el paso inverso de `decrease_stock`.

    Solo actúa si el pedido está en uno de `estados_permitidos`; el bloqueo de
    la fila (FOR UPDATE) evita que dos peticiones simultáneas devuelvan el
    stock dos veces. Si se pasa `usuario_id`, el pedido debe pertenecerle
    (comprador). Devuelve True si el cambio se aplicó, False en caso contrario.
    Una publicación que estaba 'Agotada' vuelve a 'Activa' al recuperar stock."""
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT estado FROM pedidos WHERE id = %s"
        params = [pedido_id]
        if usuario_id is not None:
            query += " AND usuario_id = %s"
            params.append(usuario_id)
        cursor.execute(query + " FOR UPDATE", tuple(params))
        pedido = cursor.fetchone()
        if not pedido or pedido['estado'] not in estados_permitidos:
            conn.rollback()
            return False

        cursor.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (nuevo_estado, pedido_id))
        cursor.execute(
            "SELECT publicacion_id, SUM(cantidad) AS cantidad FROM detalle_pedidos "
            "WHERE pedido_id = %s GROUP BY publicacion_id", (pedido_id,)
        )
        for item in cursor.fetchall():
            cursor.execute(
                "UPDATE publicaciones SET cantidad_disponible = cantidad_disponible + %s WHERE id = %s",
                (item['cantidad'], item['publicacion_id'])
            )
            cursor.execute(
                "UPDATE publicaciones SET estado = 'Activa' "
                "WHERE id = %s AND estado = 'Agotada' AND cantidad_disponible > 0",
                (item['publicacion_id'],)
            )
        conn.commit()
        return True
    except Error as e:
        print(f"Release order error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_order_details(pedido_id):
    return query_db("""
        SELECT dp.*, p.titulo, p.unidad_medida,
               u.nombre as campesino_nombre
        FROM detalle_pedidos dp
        JOIN publicaciones p ON dp.publicacion_id = p.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        WHERE dp.pedido_id = %s
    """, (pedido_id,))

def _parse_productos_pedido(raw):
    """Convierte el string armado por GROUP_CONCAT/CONCAT_WS (formato
    'titulo|cantidad|precio_unitario|unidad;;titulo|cantidad|precio_unitario|unidad;;...')
    en una lista de dicts lista para usar en la plantilla."""
    if not raw:
        return []
    items = []
    for chunk in raw.split(';;'):
        partes = chunk.split('|')
        if len(partes) != 4:
            continue
        titulo, cantidad, precio_unitario, unidad = partes
        try:
            cantidad = float(cantidad)
            if cantidad == int(cantidad):
                cantidad = int(cantidad)
        except (TypeError, ValueError):
            pass
        items.append({
            'titulo': titulo,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'unidad_medida': unidad,
        })
    return items


def get_orders_by_user(usuario_id, filters=None):
    """Pedidos hechos POR un comprador (empresa o comerciante), con el
    detalle (nombre, cantidad y precio) de cada producto pedido."""
    filters = filters or {}
    query = """
        SELECT p.*,
               GROUP_CONCAT(DISTINCT CONCAT_WS('|', pub.titulo, dp.cantidad, dp.precio_unitario, pub.unidad_medida)
                            ORDER BY pub.titulo SEPARATOR ';;') AS productos_raw
        FROM pedidos p
        LEFT JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        LEFT JOIN publicaciones pub ON dp.publicacion_id = pub.id
        WHERE p.usuario_id = %s
    """
    params = [usuario_id]
    if filters.get('estado') in ESTADOS_PEDIDO:
        query += " AND p.estado = %s"
        params.append(filters['estado'])
    query += " GROUP BY p.id ORDER BY p.fecha_pedido DESC"
    orders = query_db(query, tuple(params)) or []
    for order in orders:
        order['productos_detalle'] = _parse_productos_pedido(order.pop('productos_raw', None))
    return orders
