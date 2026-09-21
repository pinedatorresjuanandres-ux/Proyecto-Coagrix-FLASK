from database import query_db, execute_db

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

def get_farmer_publications(campesino_id):
    return query_db("""
        SELECT p.*, pr.nombre as producto_nombre, c.nombre as categoria_nombre
        FROM publicaciones p
        JOIN productos pr ON p.producto_id = pr.id
        JOIN categorias c ON pr.categoria_id = c.id
        WHERE p.campesino_id = %s
        ORDER BY p.fecha_publicacion DESC
    """, (campesino_id,))

def get_farmer_orders(campesino_id):
    return query_db("""
        SELECT p.*, u.nombre as comprador_nombre, u.email
        FROM pedidos p
        JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        JOIN publicaciones pub ON dp.publicacion_id = pub.id
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE pub.campesino_id = %s
        ORDER BY p.fecha_pedido DESC
    """, (campesino_id,))

def get_farmer_sales_stats(campesino_id):
    stats = query_db("""
        SELECT 
            COUNT(DISTINCT p.id) as total_pedidos,
            SUM(dp.cantidad * dp.precio_unitario) as ingresos_totales,
            COUNT(DISTINCT pub.id) as total_publicaciones
        FROM publicaciones pub
        LEFT JOIN detalle_pedidos dp ON pub.id = dp.publicacion_id
        LEFT JOIN pedidos p ON dp.pedido_id = p.id
        WHERE pub.campesino_id = %s
    """, (campesino_id,), one=True)
    return stats if stats else {'total_pedidos': 0, 'ingresos_totales': 0, 'total_publicaciones': 0}
