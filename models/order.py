from database import query_db, execute_db

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

def get_order_details(pedido_id):
    return query_db("""
        SELECT dp.*, p.titulo, p.precio, p.unidad_medida,
               u.nombre as campesino_nombre
        FROM detalle_pedidos dp
        JOIN publicaciones p ON dp.publicacion_id = p.id
        JOIN campesinos ca ON p.campesino_id = ca.id
        JOIN usuarios u ON ca.usuario_id = u.id
        WHERE dp.pedido_id = %s
    """, (pedido_id,))

def get_orders_by_user(usuario_id):
    """Pedidos hechos POR un comprador (empresa o comerciante), con el total
    de artículos de cada uno."""
    return query_db("""
        SELECT p.*, COUNT(dp.id) as items_count
        FROM pedidos p
        LEFT JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        WHERE p.usuario_id = %s
        GROUP BY p.id
        ORDER BY p.fecha_pedido DESC
    """, (usuario_id,))
