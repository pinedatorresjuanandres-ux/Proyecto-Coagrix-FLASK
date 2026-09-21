"""Comentarios de usuarios en la sección Testimonios de la página de inicio.
Modelos mockeados (sin MySQL real)."""
import pytest
from extensions import limiter

import app as app_module
import Controlador.comment_controller as comments
import Modelo.comment as comment_model

COMENTARIOS = [
    {'id': 1, 'texto': 'Muy buena plataforma', 'nombre': 'Juan Campesino', 'rol': 'Campesino', 'municipio': 'Marinilla'},
    {'id': 2, 'texto': 'Nos ahorra logística', 'nombre': 'AgroExport S.A.S', 'rol': 'Empresa', 'municipio': None},
]


@pytest.fixture(autouse=True)
def _reset_limits():
    limiter.reset()


@pytest.fixture
def home(monkeypatch):
    monkeypatch.setattr(app_module, 'get_public_comments', lambda: COMENTARIOS)
    monkeypatch.setattr(app_module, 'get_user_comment', lambda uid: None)


def test_inicio_muestra_comentarios_con_rol_y_municipio(client, home):
    html = client.get('/').get_data(as_text=True)
    assert 'Muy buena plataforma' in html
    assert 'tc-role--campesino">Campesino<' in html and '📍 Marinilla' in html
    assert 'AgroExport S.A.S' in html and 'tc-role--empresa">Empresa<' in html
    assert html.count('class="tc-place"') == 1  # sin municipio no se dibuja el 📍 vacío
    assert html.count('class="testimonial-card"') == 2
    assert 'id="tcPrev"' in html and 'id="tcNext"' in html  # los dos botones de navegación


def test_inicio_escapa_el_html_de_los_comentarios(client, monkeypatch):
    monkeypatch.setattr(app_module, 'get_public_comments',
                        lambda: [{**COMENTARIOS[0], 'texto': '<script>alert(1)</script>'}])
    monkeypatch.setattr(app_module, 'get_user_comment', lambda uid: None)
    html = client.get('/').get_data(as_text=True)
    assert '<script>alert(1)</script>' not in html and '&lt;script&gt;' in html


def test_sin_comentarios_muestra_mensaje(client, monkeypatch):
    monkeypatch.setattr(app_module, 'get_public_comments', lambda: [])
    monkeypatch.setattr(app_module, 'get_user_comment', lambda uid: None)
    html = client.get('/').get_data(as_text=True)
    assert 'Sé el primero' in html and 'id="tcPrev"' not in html


def test_invitado_no_ve_formulario_ni_invitacion(client, home):
    html = client.get('/').get_data(as_text=True)
    assert 'tc-form-card' not in html and 'name="texto"' not in html
    assert '¿Ya usas CoAgrix?' not in html and 'Inicia sesión para dejar' not in html
    assert 'Muy buena plataforma' in html  # los comentarios siguen visibles para todos


def test_usuario_logueado_ve_el_formulario(client, home, login_as):
    login_as(user_id=2, user_name='Juan Campesino')
    html = client.get('/').get_data(as_text=True)
    assert 'name="texto"' in html and 'Publicar comentario' in html and 'Eliminar mi comentario' not in html


def test_usuario_con_comentario_puede_editarlo_o_eliminarlo(client, monkeypatch, login_as):
    monkeypatch.setattr(app_module, 'get_public_comments', lambda: COMENTARIOS)
    monkeypatch.setattr(app_module, 'get_user_comment', lambda uid: {'id': 1, 'texto': 'Mi texto previo', 'estado': 'Publicado'})
    login_as(user_id=2)
    html = client.get('/').get_data(as_text=True)
    assert 'Mi texto previo' in html and 'Actualizar comentario' in html and 'Eliminar mi comentario' in html


def test_publicar_requiere_sesion(client, monkeypatch):
    saved = []
    monkeypatch.setattr(comments, 'save_comment', lambda uid, t: saved.append((uid, t)) or True)
    resp = client.post('/comentarios', data={'texto': 'Un comentario válido'})
    assert resp.status_code == 302 and '/login' in resp.headers['Location'] and saved == []


def test_publicar_guarda_el_texto_limpio(client, login_as, monkeypatch):
    login_as(user_id=4)
    saved = []
    monkeypatch.setattr(comments, 'save_comment', lambda uid, t: saved.append((uid, t)) or True)
    resp = client.post('/comentarios', data={'texto': '  Me ayuda   mucho\n con   mis ventas  '})
    assert resp.status_code == 302 and resp.headers['Location'].endswith('/#testimonios')
    assert saved == [(4, 'Me ayuda mucho con mis ventas')]


@pytest.mark.parametrize('texto', ['', '   ', 'corto', 'x' * 301])
def test_publicar_rechaza_textos_invalidos(client, login_as, monkeypatch, texto):
    login_as(user_id=4)
    saved = []
    monkeypatch.setattr(comments, 'save_comment', lambda uid, t: saved.append(t) or True)
    client.post('/comentarios', data={'texto': texto})
    assert saved == []


def test_eliminar_borra_solo_el_comentario_propio(client, login_as, monkeypatch):
    login_as(user_id=4)
    deleted = []
    monkeypatch.setattr(comments, 'delete_user_comment', lambda uid: deleted.append(uid))
    # aunque se intente mandar otro usuario, se usa siempre el de la sesión
    client.post('/comentarios/eliminar', data={'usuario_id': 99})
    assert deleted == [4]


def test_modelo_un_comentario_por_usuario_y_conserva_el_estado(monkeypatch):
    captured = {}
    monkeypatch.setattr(comment_model, 'execute_db', lambda q, args: captured.update(q=' '.join(q.split()), args=args) or 1)
    comment_model.save_comment(4, 'Hola mundo')
    assert 'ON DUPLICATE KEY UPDATE texto = VALUES(texto)' in captured['q']
    assert 'estado' not in captured['q'].split('ON DUPLICATE')[1]  # editar no des-oculta
    assert captured['args'] == (4, 'Hola mundo')


def test_modelo_solo_lista_comentarios_publicados_de_usuarios_activos(monkeypatch):
    captured = {}
    monkeypatch.setattr(comment_model, 'query_db', lambda q, args=(), one=False: captured.update(q=' '.join(q.split()), args=args) or [])
    comment_model.get_public_comments(5)
    assert "c.estado = 'Publicado'" in captured['q'] and "u.estado = 'Activo'" in captured['q']
    assert captured['args'] == (5,)
