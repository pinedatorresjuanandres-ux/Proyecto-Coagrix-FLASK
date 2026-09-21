"""1) Un producto agotado vuelve al catálogo cuando su dueño le repone cantidad.
2) El administrador gestiona (edita, oculta/publica, elimina) los comentarios
del inicio. Base de datos mockeada."""
import pytest

import Controlador.admin_controller as admin_routes
import Controlador.farmer_controller as farmer_routes
import Modelo.comment as comment_model
import Modelo.product as product_model


# ---------------- Producto agotado que se vuelve a mostrar ----------------

def test_al_editar_se_sincroniza_el_estado_con_la_cantidad(monkeypatch):
    sqls = []
    monkeypatch.setattr(product_model, 'query_db', lambda *a, **k: {'precio_empresa': 10, 'precio_comerciante': 10})
    monkeypatch.setattr(product_model, 'execute_db', lambda q, args=(): sqls.append((' '.join(q.split()), args)) or True)
    product_model.update_publication(7, 1, 'Papa', 'desc', 10, 10, 50, 'kg')
    reactivar = [s for s, a in sqls if s.startswith("UPDATE publicaciones SET estado = 'Activa'")]
    agotar = [s for s, a in sqls if s.startswith("UPDATE publicaciones SET estado = 'Agotada'")]
    # Solo una Agotada con cantidad > 0 pasa a Activa; una Inactiva (ocultada por el admin) no se toca.
    assert reactivar and "estado = 'Agotada' AND cantidad_disponible > 0" in reactivar[0]
    assert agotar and "estado = 'Activa' AND cantidad_disponible <= 0" in agotar[0]
    assert all("'Inactiva'" not in s for s, a in sqls)


def test_no_se_sincroniza_si_el_guardado_falla(monkeypatch):
    sqls = []
    monkeypatch.setattr(product_model, 'query_db', lambda *a, **k: None)
    monkeypatch.setattr(product_model, 'execute_db', lambda q, args=(): sqls.append(q) or False)
    product_model.update_publication(7, 1, 'Papa', 'd', 10, 10, 50, 'kg')
    assert len(sqls) == 1  # solo el UPDATE principal


def test_editar_una_agotada_con_stock_avisa_que_vuelve_al_catalogo(client, login_as, monkeypatch):
    login_as(user_id=1, role_name='Campesino', role_id=2)
    estados = iter([{'campesino_id': 9, 'estado': 'Agotada', 'imagen': None},
                    {'campesino_id': 9, 'estado': 'Activa', 'imagen': None}])
    monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 9})
    monkeypatch.setattr(farmer_routes, 'get_publication_by_id', lambda pid: next(estados))
    monkeypatch.setattr(farmer_routes, 'get_or_create_producto', lambda *a: 1)
    monkeypatch.setattr(farmer_routes, '_save_image', lambda f: None)
    monkeypatch.setattr(farmer_routes, 'update_publication', lambda *a, **k: True)
    resp = client.post('/farmer/publicaciones/7/editar', data={
        'nombre_producto': 'Papa', 'categoria_id': '1', 'precio_empresa': '10', 'precio_comerciante': '10',
        'cantidad': '50', 'unidad': 'kg'}, follow_redirects=False)
    assert resp.status_code == 302
    with client.session_transaction() as s:
        msgs = [m for _, m in s.get('_flashes', [])]
    assert any('volvió a estar disponible en el catálogo' in m for m in msgs)


# ---------------- Panel de comentarios del administrador ----------------

@pytest.fixture
def admin(client, login_as):
    login_as(user_id=1, role_name='Administrador', role_id=1)
    return client


def test_solo_el_admin_ve_el_panel_de_comentarios(client, login_as):
    login_as(user_id=2, role_name='Campesino', role_id=2)
    for method in (client.get, client.post):
        resp = method('/admin/comentarios') if method == client.get else method('/admin/comentarios/1/eliminar')
        assert resp.status_code == 302 and '/login' in resp.headers['Location']


def test_el_admin_ve_todos_los_comentarios_con_autor_y_estado(admin, monkeypatch):
    rows = [
        {'id': 1, 'texto': 'Muy buena plataforma', 'estado': 'Publicado', 'creado_en': '2026-09-20', 'actualizado_en': '2026-09-20',
         'nombre': 'Juan Campesino', 'email': 'campesino@coagrix.com', 'rol': 'Campesino'},
        {'id': 2, 'texto': 'Comentario oculto de prueba', 'estado': 'Oculto', 'creado_en': '2026-09-19', 'actualizado_en': '2026-09-19',
         'nombre': 'Pedro', 'email': 'p@coagrix.com', 'rol': 'Comerciante'},
    ]
    monkeypatch.setattr(admin_routes, 'list_comments_for_admin', lambda f, page, per_page: (rows, 2))
    html = admin.get('/admin/comentarios').get_data(as_text=True)
    assert 'Muy buena plataforma' in html and 'campesino@coagrix.com' in html
    assert 'Comentario oculto de prueba' in html and 'Oculto' in html
    assert '/admin/comentarios/1/editar' in html and '/admin/comentarios/2/eliminar' in html
    assert 'Ocultar' in html and 'Publicar' in html


def test_admin_edita_un_comentario(admin, monkeypatch):
    saved = []
    monkeypatch.setattr(admin_routes, 'admin_update_comment', lambda cid, t: saved.append((cid, t)) or True)
    resp = admin.post('/admin/comentarios/5/editar', data={'texto': '  Texto   corregido por el admin  '})
    assert resp.status_code == 302 and saved == [(5, 'Texto corregido por el admin')]


@pytest.mark.parametrize('texto', ['', 'corto', 'x' * 301])
def test_admin_no_puede_guardar_textos_invalidos(admin, monkeypatch, texto):
    saved = []
    monkeypatch.setattr(admin_routes, 'admin_update_comment', lambda cid, t: saved.append(t) or True)
    admin.post('/admin/comentarios/5/editar', data={'texto': texto})
    assert saved == []


def test_admin_oculta_y_publica(admin, monkeypatch):
    calls = []
    monkeypatch.setattr(admin_routes, 'admin_set_comment_status', lambda cid, e: calls.append((cid, e)) or True)
    admin.post('/admin/comentarios/5/estado', data={'estado': 'Oculto'})
    admin.post('/admin/comentarios/5/estado', data={'estado': 'Publicado'})
    assert calls == [(5, 'Oculto'), (5, 'Publicado')]


def test_estado_invalido_no_se_acepta():
    assert comment_model.admin_set_comment_status(5, 'Borrado') is False


def test_admin_elimina_un_comentario(admin, monkeypatch):
    deleted = []
    monkeypatch.setattr(admin_routes, 'admin_delete_comment', lambda cid: deleted.append(cid))
    resp = admin.post('/admin/comentarios/5/eliminar')
    assert resp.status_code == 302 and deleted == [5]


def test_consulta_de_admin_incluye_ocultos_y_filtra(monkeypatch):
    captured = []
    monkeypatch.setattr(comment_model, 'query_db',
                        lambda q, args=(), one=False: captured.append((' '.join(q.split()), args)) or ({'total': 0} if one else []))
    comment_model.list_comments_for_admin({'buscar': 'ana', 'estado': 'Oculto'}, page=2, per_page=20)
    count_sql, _ = captured[0]
    select_sql, select_args = captured[1]
    assert "c.estado = 'Publicado'" not in select_sql  # a diferencia de la página pública, trae también los ocultos
    assert 'c.estado = %s' in select_sql and 'LIKE' in select_sql
    assert select_args[-2:] == (20, 20)  # LIMIT 20 OFFSET 20 (página 2)
    assert count_sql.startswith('SELECT COUNT(*)')


def test_el_menu_del_admin_enlaza_a_comentarios(admin, monkeypatch):
    monkeypatch.setattr(admin_routes, 'list_comments_for_admin', lambda f, page, per_page: ([], 0))
    assert '/admin/comentarios' in admin.get('/admin/comentarios').get_data(as_text=True)
