"""Pruebas de que un usuario no puede ver ni operar pedidos ajenos (IDOR)
cambiando el id en la URL. Se mockea la capa de modelos (base de datos)
para no depender de un MySQL real: lo que se verifica es que las rutas
llaman a las funciones de verificación de propiedad y respetan su
resultado, no el SQL en sí.
"""
import routes.farmer_routes as farmer_routes
import controllers.cart_controller as cart_controller


def test_farmer_cannot_view_foreign_order(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino')

    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 99})
    monkeypatch.setattr(farmer_routes, 'order_belongs_to_farmer', lambda pedido_id, campesino_id: False)

    resp = client.get('/farmer/pedidos/123')
    assert resp.status_code == 403


def test_farmer_can_view_own_order(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino')

    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 99})
    monkeypatch.setattr(farmer_routes, 'order_belongs_to_farmer', lambda pedido_id, campesino_id: True)
    monkeypatch.setattr(farmer_routes, 'get_order_details', lambda pedido_id: [])
    monkeypatch.setattr(farmer_routes, 'get_order', lambda pedido_id: {'id': pedido_id, 'estado': 'Pendiente'})

    resp = client.get('/farmer/pedidos/123')
    assert resp.status_code == 200


def test_farmer_cannot_accept_foreign_order(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino')

    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 99})
    monkeypatch.setattr(farmer_routes, 'order_belongs_to_farmer', lambda pedido_id, campesino_id: False)

    called = {}

    def fake_update(pedido_id, estado):
        called['called'] = True

    monkeypatch.setattr(farmer_routes, 'update_order_status', fake_update)

    resp = client.post('/farmer/pedidos/123/aceptar')
    assert resp.status_code == 403
    assert 'called' not in called  # nunca debe llegar a cambiar el estado


def test_buyer_cannot_view_foreign_order(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Empresa')

    monkeypatch.setattr(cart_controller, 'get_order_for_buyer', lambda pedido_id, usuario_id: None)

    resp = client.get('/carrito/pedidos/456')
    assert resp.status_code == 403


def test_buyer_can_view_own_order(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Empresa')

    monkeypatch.setattr(cart_controller, 'get_order_for_buyer',
                         lambda pedido_id, usuario_id: {'id': pedido_id, 'usuario_id': usuario_id})
    monkeypatch.setattr(cart_controller, 'get_order_details', lambda pedido_id: [])

    resp = client.get('/carrito/pedidos/456')
    assert resp.status_code == 200
