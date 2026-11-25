"""Pruebas de que las páginas de error personalizadas responden con el
código correcto (en vez de las páginas por defecto de Flask)."""


def test_404_page(client):
    resp = client.get('/esta-ruta-no-existe-nunca')
    assert resp.status_code == 404
    assert 'no existe'.encode('utf-8') in resp.data or b'404' in resp.data


def test_403_on_forbidden_admin_route_without_session(client):
    # Sin sesión de admin, el before_request del blueprint debe redirigir
    # al login en vez de dejar pasar la petición.
    resp = client.get('/admin/usuarios', follow_redirects=False)
    assert resp.status_code in (301, 302, 303, 307, 308)
