"""Comparar precios: buscador de producto. La tabla solo aparece al buscar
(o al pedir ver todos) y muestra únicamente lo que coincide."""
import pytest

import Controlador.farmer_controller as farmer_routes
import Controlador.company_controller as company_routes
import Controlador.merchant_controller as merchant_routes
import Modelo.product as product_model

ITEM = {'producto_id': 1, 'nombre': 'Café Pergamino', 'precio_min': 15500, 'precio_max': 15500, 'num_vendedores': 1}
ITEM2 = {'producto_id': 2, 'nombre': 'Mango', 'precio_min': 3000, 'precio_max': 4500, 'num_vendedores': 2}

ROLES = [
    ('/farmer/comparar', farmer_routes, dict(role_name='Campesino', role_id=2)),
    ('/company/comparar', company_routes, dict(role_name='Empresa', role_id=3)),
    ('/merchant/comparar', merchant_routes, dict(role_name='Comerciante', role_id=4)),
]


@pytest.fixture(params=ROLES, ids=['campesino', 'empresa', 'comerciante'])
def page(request, client, login_as, monkeypatch):
    url, module, role = request.param
    login_as(user_id=1, **role)
    calls = []
    monkeypatch.setattr(module, 'get_price_comparison', lambda field, buscar: calls.append((field, buscar)) or [ITEM, ITEM2])
    monkeypatch.setattr(module, 'get_products_with_history', lambda: [])
    return client, url, calls


def test_sin_buscar_no_se_lista_ni_consulta_nada(page):
    client, url, calls = page
    html = client.get(url).get_data(as_text=True)
    assert calls == []
    assert '¿Qué producto quieres comparar?' in html
    assert 'Café Pergamino' not in html


def test_buscar_muestra_la_tabla_con_los_resultados(page):
    client, url, calls = page
    html = client.get(url, query_string={'buscar': ' caf '}).get_data(as_text=True)
    assert calls[0][1] == 'caf'
    assert 'Café Pergamino' in html and '2 vendedores' in html and '1 vendedor<' in html


def test_ver_todos_lista_sin_filtro(page):
    client, url, calls = page
    html = client.get(url, query_string={'todos': 1}).get_data(as_text=True)
    assert calls[0][1] == ''
    assert 'Mango' in html


def test_cada_rol_compara_con_su_precio(page):
    client, url, calls = page
    client.get(url, query_string={'buscar': 'x'})
    esperado = 'precio_empresa' if 'company' in url else 'precio_comerciante'
    assert calls[0][0] == esperado


def test_sin_resultados_muestra_mensaje(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino', role_id=2)
    monkeypatch.setattr(farmer_routes, 'get_price_comparison', lambda f, b: [])
    monkeypatch.setattr(farmer_routes, 'get_products_with_history', lambda: [])
    html = client.get('/farmer/comparar?buscar=zzz').get_data(as_text=True)
    assert 'No encontramos "zzz"' in html


def test_consulta_filtra_por_nombre_y_escapa_comodines(monkeypatch):
    captured = {}
    monkeypatch.setattr(product_model, 'query_db',
                        lambda sql, params=(), one=False: captured.update(sql=' '.join(sql.split()), params=params) or [])
    product_model.get_price_comparison('precio_empresa', '50%_off')
    assert "pr.nombre LIKE %s ESCAPE '!'" in captured['sql']
    assert 'MIN(p.precio_empresa)' in captured['sql']
    assert captured['params'] == ('%50!%!_off%',)


def test_consulta_sin_buscar_no_filtra_y_valida_la_columna(monkeypatch):
    captured = {}
    monkeypatch.setattr(product_model, 'query_db',
                        lambda sql, params=(), one=False: captured.update(sql=' '.join(sql.split()), params=params) or [])
    product_model.get_price_comparison('precio_inventado; DROP TABLE x')
    assert 'LIKE' not in captured['sql'] and captured['params'] == ()
    assert 'MIN(p.precio_comerciante)' in captured['sql'] and 'DROP' not in captured['sql']
