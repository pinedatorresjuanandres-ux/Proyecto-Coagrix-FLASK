"""Los pedidos del panel del campesino se listan por orden de llegada
(número de pedido descendente), sin depender de `fecha_pedido`."""
import Modelo.farmer as farmer_model


def test_pedidos_del_campesino_van_por_orden_de_llegada(monkeypatch):
    captured = {}

    def fake_query(sql, params=(), one=False):
        captured['sql'] = ' '.join(sql.split())
        return []

    monkeypatch.setattr(farmer_model, 'query_db', fake_query)
    farmer_model.get_farmer_orders(5, {'estado': 'Pendiente'})
    assert captured['sql'].endswith('ORDER BY p.id DESC')
