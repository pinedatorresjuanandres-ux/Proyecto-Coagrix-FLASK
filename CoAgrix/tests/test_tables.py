"""Tablas unificadas: todas usan el mismo estilo (cx-table dentro de cx-table-wrap),
las etiquetas de estado salen de un solo componente, y el detalle de pedido
no falla al multiplicar cantidad (float) por precio (Decimal)."""
import pathlib
import re
from decimal import Decimal

import pytest

import Controlador.cart_controller as cart_controller
import Controlador.farmer_controller as farmer_routes

VISTA = pathlib.Path(__file__).resolve().parent.parent / 'Vista'
TABLE_TAG = re.compile(r'<table\b([^>]*)>')


def _templates():
    return sorted(VISTA.rglob('*.html'))


def test_ninguna_tabla_lleva_estilo_en_linea():
    for path in _templates():
        for attrs in TABLE_TAG.findall(path.read_text(encoding='utf-8')):
            assert 'style=' not in attrs, f'{path.name}: la tabla debe usar clases, no style en línea'


def test_todas_las_tablas_usan_una_clase_del_sistema():
    for path in _templates():
        for attrs in TABLE_TAG.findall(path.read_text(encoding='utf-8')):
            assert 'cx-table' in attrs or 'pc-table' in attrs, f'{path.name}: tabla sin clase cx-table/pc-table'


def test_las_tablas_de_datos_van_dentro_de_su_tarjeta_con_scroll():
    for path in _templates():
        text = path.read_text(encoding='utf-8')
        if 'class="cx-table"' in text and path.parent.name not in ('admin', 'messages'):
            # admin y mensajes ya las envuelven en `cx-card` con overflow-x
            assert 'cx-table-wrap' in text, f'{path.name}: falta el contenedor cx-table-wrap'


def test_base_carga_el_estilo_de_tablas_despues_del_rediseno():
    base = (VISTA / 'base.html').read_text(encoding='utf-8')
    assert base.index('coagrix-redesign.css') < base.index('tables.css')


@pytest.mark.parametrize('estado,clase', [
    ('Completado', 'success'), ('Aceptado', 'info'), ('Pendiente', 'warning'),
    ('Rechazado', 'danger'), ('Cancelado', 'neutral'), ('Otro', 'neutral'),
])
def test_etiqueta_de_estado_unica(app, estado, clase):
    tpl = app.jinja_env.from_string("{% from 'components/badges.html' import estado_pedido %}{{ estado_pedido(e) }}")
    html = tpl.render(e=estado)
    assert f'cx-badge-status cx-badge-{clase}' in html and estado in html


DETALLES = [{'titulo': 'Café', 'unidad_medida': 'kg', 'campesino_nombre': 'Juan',
             'cantidad': 50.0, 'precio_unitario': Decimal('22000.00')}]  # float x Decimal: antes daba TypeError


def test_detalle_de_pedido_del_campesino_calcula_el_subtotal(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino', role_id=2)
    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 9})
    monkeypatch.setattr(farmer_routes, 'order_belongs_to_farmer', lambda p, c: True)
    monkeypatch.setattr(farmer_routes, 'get_order_details', lambda p: DETALLES)
    monkeypatch.setattr(farmer_routes, 'get_order', lambda p: {'id': p, 'estado': 'Completado'})
    resp = client.get('/farmer/pedidos/8')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200 and '1.100.000' in html and 'cx-badge-success' in html


def test_detalle_de_pedido_del_comprador_calcula_el_subtotal(client, login_as, monkeypatch):
    login_as(user_id=3, role_name='Empresa', role_id=3)
    monkeypatch.setattr(cart_controller, 'get_order_for_buyer', lambda p, u: {'id': p, 'estado': 'Pendiente'})
    monkeypatch.setattr(cart_controller, 'get_order_details', lambda p: DETALLES)
    resp = client.get('/carrito/pedidos/2')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200 and '1.100.000' in html and 'cx-badge-warning' in html
