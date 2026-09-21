"""Pruebas de la cancelación de pedidos y de la devolución de stock. La base
de datos se simula con un cursor falso que registra el SQL ejecutado."""
import Controlador.cart_controller as cart
import Modelo.order as order_model


class FakeCursor:
    def __init__(self, estado, detalles):
        self.estado, self.detalles = estado, detalles
        self.executed, self._last = [], None

    def execute(self, sql, params=()):
        self.executed.append((' '.join(sql.split()), params))
        self._last = sql

    def fetchone(self):
        return {'estado': self.estado} if self.estado else None

    def fetchall(self):
        return self.detalles

    def close(self):
        pass


class FakeConn:
    def __init__(self, cursor):
        self.cur, self.commits, self.rollbacks = cursor, 0, 0

    def cursor(self, dictionary=False):
        return self.cur

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        pass


def _release(monkeypatch, estado, allowed=('Pendiente', 'Aceptado'), usuario_id=7):
    cur = FakeCursor(estado, [{'publicacion_id': 3, 'cantidad': 4.0}, {'publicacion_id': 5, 'cantidad': 1.5}])
    conn = FakeConn(cur)
    monkeypatch.setattr(order_model, 'get_db_connection', lambda: conn)
    ok = order_model.release_order(1, 'Cancelado', allowed, usuario_id=usuario_id)
    return ok, cur, conn


def test_cancelar_devuelve_stock_de_cada_publicacion(monkeypatch):
    ok, cur, conn = _release(monkeypatch, 'Pendiente')
    assert ok and conn.commits == 1 and conn.rollbacks == 0
    sqls = [s for s, _ in cur.executed]
    assert any('UPDATE pedidos SET estado' in s for s in sqls)
    restores = [p for s, p in cur.executed if 'cantidad_disponible = cantidad_disponible + %s' in s]
    assert restores == [(4.0, 3), (1.5, 5)]
    assert sum("estado = 'Activa'" in s and "'Agotada'" in s for s in sqls) == 2


def test_no_se_cancela_dos_veces_ni_un_pedido_completado(monkeypatch):
    for estado in ('Cancelado', 'Completado', 'Rechazado', None):
        ok, cur, conn = _release(monkeypatch, estado)
        assert not ok and conn.commits == 0 and conn.rollbacks == 1
        assert not any(s.startswith('UPDATE') for s, _ in cur.executed)


def test_ruta_cancelar_exige_ser_el_comprador(client, login_as, monkeypatch):
    login_as(user_id=7, role_id=3, role_name='Empresa')
    monkeypatch.setattr(cart, 'get_order_for_buyer', lambda pid, uid: None)
    called = {}
    monkeypatch.setattr(cart, 'release_order', lambda *a, **k: called.setdefault('x', True))
    assert client.post('/carrito/pedidos/9/cancelar').status_code == 403
    assert not called


def test_ruta_cancelar_llama_release_order(client, login_as, monkeypatch):
    login_as(user_id=7, role_id=4, role_name='Comerciante')
    monkeypatch.setattr(cart, 'get_order_for_buyer', lambda pid, uid: {'id': pid})
    args = {}
    monkeypatch.setattr(cart, 'release_order',
                        lambda pid, estado, permitidos, usuario_id=None: args.update(pid=pid, estado=estado, uid=usuario_id) or True)
    resp = client.post('/carrito/pedidos/9/cancelar')
    assert resp.status_code == 302
    assert args == {'pid': 9, 'estado': 'Cancelado', 'uid': 7}
