"""Hay un solo login (/login); el registro sigue ofreciendo los 3 perfiles."""
import pytest


def test_login_es_un_solo_formulario(client):
    html = client.get('/login').get_data(as_text=True)
    assert html.count('<form') == 1
    assert 'name="email"' in html and 'name="password"' in html
    assert 'Soy Campesino' not in html and 'Soy Empresa' not in html  # ya no hay tarjetas de perfil
    assert '/olvide-contrasena' in html
    assert 'href="/register"' in html  # "Regístrate" lleva a elegir perfil


@pytest.mark.parametrize('url', ['/login/campesino', '/login/empresa', '/login/comerciante'])
def test_urls_antiguas_redirigen_al_login_unico(client, url):
    resp = client.get(url)
    assert resp.status_code == 302 and resp.headers['Location'].endswith('/login')


def test_registro_sigue_mostrando_los_tres_perfiles(client):
    html = client.get('/register').get_data(as_text=True)
    for ruta in ('/register/campesino', '/register/empresa', '/register/comerciante'):
        assert ruta in html
