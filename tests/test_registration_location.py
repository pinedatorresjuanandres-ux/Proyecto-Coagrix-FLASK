"""Pruebas del desplegable Departamento -> Municipio del registro y de que
lo elegido se guarda en `ubicaciones`. La capa de modelos se mockea para no
depender de un MySQL real."""
import pytest

import Controlador.auth_controller as auth
import Modelo.ubicaciones as ubicaciones

FORM = {
    'nombre': 'Juan Perez', 'email': 'juan@example.com', 'telefono': '3101234567',
    'departamento': 'Antioquia', 'municipio': 'Marinilla', 'direccion': 'Vereda La Esperanza',
    'password': 'Abcdefg1', 'password_confirm': 'Abcdefg1',
}


CATALOGO = {'Antioquia': ['Marinilla', 'Medellín'], 'Huila': ['Neiva']}


def test_catalogo_agrupa_municipios_por_departamento(monkeypatch):
    rows = [{'departamento': d, 'municipio': m} for d, ms in CATALOGO.items() for m in ms]
    monkeypatch.setattr(ubicaciones, 'query_db', lambda *a, **k: rows)
    assert ubicaciones.get_ubicaciones_colombia() == CATALOGO


def test_catalogo_vacio_si_falla_la_base(monkeypatch):
    monkeypatch.setattr(ubicaciones, 'query_db', lambda *a, **k: None)
    assert ubicaciones.get_ubicaciones_colombia() == {}


def test_is_valid_location_consulta_departamento_y_municipio(monkeypatch):
    calls = []
    monkeypatch.setattr(ubicaciones, 'query_db', lambda q, args, one=False: calls.append(args) or {'1': 1})
    assert ubicaciones.is_valid_location('Antioquia', 'Marinilla')
    assert calls == [('Antioquia', 'Marinilla')]
    monkeypatch.setattr(ubicaciones, 'query_db', lambda *a, **k: None)
    assert not ubicaciones.is_valid_location('Antioquia', 'Neiva')


@pytest.mark.parametrize('url', ['/register/campesino', '/register/empresa', '/register/comerciante'])
def test_registro_muestra_desplegables(client, monkeypatch, url):
    monkeypatch.setattr(auth, 'get_ubicaciones_colombia', lambda: CATALOGO)
    html = client.get(url).get_data(as_text=True)
    assert '<select id="departamento" name="departamento"' in html
    assert '<select id="municipio" name="municipio"' in html
    assert '<option value="Huila">' in html


def _mock_models(monkeypatch, saved):
    monkeypatch.setattr(auth, 'get_user_by_email', lambda email: None)
    monkeypatch.setattr(auth, 'create_user', lambda *a: 10)
    monkeypatch.setattr(auth, 'create_location', lambda dep, mun, direccion=None: saved.update(dep=dep, mun=mun) or 5)
    monkeypatch.setattr(auth, 'create_farmer_profile', lambda *a: True)
    monkeypatch.setattr(auth, 'is_valid_location', lambda dep, mun: mun in CATALOGO.get(dep, []))


def test_registro_guarda_departamento_y_municipio(client, monkeypatch):
    saved = {}
    _mock_models(monkeypatch, saved)
    resp = client.post('/register/campesino', data=FORM)
    assert resp.status_code == 302
    assert saved == {'dep': 'Antioquia', 'mun': 'Marinilla'}


def test_registro_rechaza_municipio_de_otro_departamento(client, monkeypatch):
    saved = {}
    _mock_models(monkeypatch, saved)
    resp = client.post('/register/campesino', data={**FORM, 'municipio': 'Neiva'})
    assert resp.status_code == 302
    assert saved == {}
