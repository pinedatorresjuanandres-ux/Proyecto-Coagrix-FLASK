"""Separa pedidos ya existentes que mezclan productos de varios
campesinos, dejando un pedido por cada campesino (igual a como
Controlador/cart_controller.py:checkout() crea los pedidos nuevos desde
ahora). Es una reparación de datos de una sola vez para pedidos hechos
antes de ese cambio; no se ejecuta como parte de la app.

Para cada pedido mixto: el campesino con menor id se queda con el
pedido original (se le recalcula el total con solo sus productos), y
por cada campesino adicional se crea un pedido nuevo (mismo comprador,
misma fecha y estado) al que se le mueven sus líneas de
detalle_pedidos.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import query_db, execute_db  # noqa: E402


def main():
    pedido_ids = [row['pedido_id'] for row in (query_db(
        "SELECT DISTINCT pedido_id FROM detalle_pedidos"
    ) or [])]

    separados = 0
    for pedido_id in pedido_ids:
        detalles = query_db("""
            SELECT dp.id, dp.cantidad, dp.precio_unitario, pub.campesino_id
            FROM detalle_pedidos dp
            JOIN publicaciones pub ON dp.publicacion_id = pub.id
            WHERE dp.pedido_id = %s
        """, (pedido_id,)) or []

        campesinos = sorted(set(d['campesino_id'] for d in detalles))
        if len(campesinos) <= 1:
            continue

        pedido = query_db("SELECT * FROM pedidos WHERE id = %s", (pedido_id,), one=True)
        if not pedido:
            continue

        primero = campesinos[0]
        for campesino_id in campesinos[1:]:
            items = [d for d in detalles if d['campesino_id'] == campesino_id]
            total_nuevo = sum(float(d['cantidad']) * float(d['precio_unitario']) for d in items)

            nuevo_pedido_id = execute_db(
                "INSERT INTO pedidos (usuario_id, fecha_pedido, estado, total) VALUES (%s, %s, %s, %s)",
                (pedido['usuario_id'], pedido['fecha_pedido'], pedido['estado'], total_nuevo)
            )
            for d in items:
                execute_db("UPDATE detalle_pedidos SET pedido_id = %s WHERE id = %s", (nuevo_pedido_id, d['id']))

            print(f"  pedido #{pedido_id}: {len(items)} producto(s) del campesino {campesino_id} -> nuevo pedido #{nuevo_pedido_id}")

        items_restantes = [d for d in detalles if d['campesino_id'] == primero]
        total_restante = sum(float(d['cantidad']) * float(d['precio_unitario']) for d in items_restantes)
        execute_db("UPDATE pedidos SET total = %s WHERE id = %s", (total_restante, pedido_id))

        separados += 1
        print(f"Pedido #{pedido_id} separado (productos de {len(campesinos)} campesinos distintos).")

    if separados == 0:
        print("No había pedidos con productos de más de un campesino. Nada que hacer.")
    else:
        print(f"\nListo. Pedidos separados: {separados}. Puedes volver a correr este script sin riesgo: es idempotente.")


if __name__ == '__main__':
    main()
