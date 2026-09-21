"""Estadísticas mensuales del campesino: tabla de producto, cantidad vendida
y ganancia. Modelos mockeados (sin MySQL real)."""
from datetime import date

import pytest

import Controlador.farmer_controller as farmer_routes
import Modelo.farmer as farmer_model

ROWS = [
    {'id': 1, 'titulo': 'Papa Pastusa', 'unidad_medida': 'kg', 'cantidad_vendida': 120.0, 'ganancia': 480000},
    {'id': 2, 'titulo': 'Huevos AA', 'unidad_medida': 'cubeta', 'cantidad_vendida': 2.5, 'ganancia': 62500},
]


@pytest.fixture
def farmer_client(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino')
    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 9})
    calls = []
    monkeypatch.setattr(farmer_routes, 'get_farmer_monthly_product_sales',
                        lambda cid, desde, hasta: calls.append((cid, desde, hasta)) or ROWS)
    return client, calls


def test_tabla_muestra_producto_cantidad_y_ganancia(farmer_client):
    client, calls = farmer_client
    html = client.get('/farmer/estadisticas?mes=2026-09').get_data(as_text=True)
    assert calls == [(9, '2026-09-01', '2026-10-01')]
    assert 'Papa Pastusa' in html and '120 kg' in html and '480.000' in html
    assert 'Huevos AA' in html and '2.5 cubeta' in html
    assert 'Septiembre 2026' in html
    assert '542.500' in html  # total del mes = 480.000 + 62.500


def test_diciembre_termina_en_enero_del_anio_siguiente(farmer_client):
    client, calls = farmer_client
    client.get('/farmer/estadisticas?mes=2026-12')
    assert calls == [(9, '2026-12-01', '2027-01-01')]


@pytest.mark.parametrize('mes', ['', 'abc', '2026-13', '2026-00', '0000-05', '1999-01', '2026-9'])
def test_mes_invalido_usa_el_mes_actual(farmer_client, mes):
    client, calls = farmer_client
    assert client.get('/farmer/estadisticas', query_string={'mes': mes}).status_code == 200
    hoy = date.today()
    assert calls[0][1] == date(hoy.year, hoy.month, 1).isoformat()


def test_mes_sin_ventas_muestra_mensaje(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino')
    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 9})
    monkeypatch.setattr(farmer_routes, 'get_farmer_monthly_product_sales', lambda *a: [])
    html = client.get('/farmer/estadisticas?mes=2026-01').get_data(as_text=True)
    assert 'No tuviste ventas completadas en Enero 2026' in html


def test_solo_el_campesino_puede_verla(client, login_as):
    login_as(user_id=2, role_name='Empresa', role_id=3)
    resp = client.get('/farmer/estadisticas')
    assert resp.status_code == 302 and '/login' in resp.headers['Location']


def test_consulta_solo_cuenta_pedidos_completados_del_mes(monkeypatch):
    captured = {}
    monkeypatch.setattr(farmer_model, 'query_db',
                        lambda sql, params=(), one=False: captured.update(sql=' '.join(sql.split()), params=params) or [])
    farmer_model.get_farmer_monthly_product_sales(9, '2026-09-01', '2026-10-01')
    assert "p.estado = 'Completado'" in captured['sql']
    assert 'p.fecha_pedido >= %s AND p.fecha_pedido < %s' in captured['sql']
    assert captured['params'] == (9, '2026-09-01', '2026-10-01')


def test_el_panel_enlaza_a_las_estadisticas(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino')
    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 9})
    monkeypatch.setattr(farmer_routes, 'get_farmer_sales_stats',
                        lambda cid: {'total_pedidos': 5, 'ingresos_totales': 1602400, 'total_publicaciones': 3})
    monkeypatch.setattr(farmer_routes, 'get_farmer_income_history', lambda cid: [])
    html = client.get('/farmer/dashboard').get_data(as_text=True)
    assert '/farmer/estadisticas' in html
