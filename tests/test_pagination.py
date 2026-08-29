"""Pruebas de la lógica de paginación agregada a get_active_publications,
list_users y list_publications_for_moderation. Se mockea query_db para
no depender de MySQL real: lo importante es verificar que se calcula bien
el total, el LIMIT/OFFSET, y que sin `page` se mantiene el comportamiento
antiguo (por compatibilidad con otros llamadores que no paginan)."""
import models.product as product_model
import models.admin as admin_model


def test_get_active_publications_without_page_returns_plain_list(monkeypatch):
    monkeypatch.setattr(product_model, 'query_db', lambda query, args=(): [{'id': 1}, {'id': 2}])

    result = product_model.get_active_publications(filters=None)

    assert result == [{'id': 1}, {'id': 2}]


def test_get_active_publications_with_page_returns_items_and_total(monkeypatch):
    calls = []

    def fake_query_db(query, args=(), one=False):
        calls.append((query, args, one))
        if 'COUNT(*)' in query:
            return {'total': 25}
        return [{'id': i} for i in range(12)]

    monkeypatch.setattr(product_model, 'query_db', fake_query_db)

    items, total = product_model.get_active_publications(filters=None, page=2, per_page=12)

    assert total == 25
    assert len(items) == 12
    # La query paginada debe incluir LIMIT/OFFSET con el offset correcto para la página 2
    paged_call = [c for c in calls if 'LIMIT' in c[0]][0]
    assert paged_call[1][-2:] == (12, 12)  # per_page=12, offset=(2-1)*12=12


def test_get_active_publications_page_clamped_to_at_least_1(monkeypatch):
    def fake_query_db(query, args=(), one=False):
        if 'COUNT(*)' in query:
            return {'total': 0}
        return []

    monkeypatch.setattr(product_model, 'query_db', fake_query_db)

    items, total = product_model.get_active_publications(filters=None, page=-5, per_page=12)
    assert total == 0
    assert items == []


def test_list_users_pagination(monkeypatch):
    def fake_query_db(query, args=(), one=False):
        if 'COUNT(*)' in query:
            return {'total': 45}
        return [{'id': i} for i in range(20)]

    monkeypatch.setattr(admin_model, 'query_db', fake_query_db)

    users, total = admin_model.list_users(filters=None, page=1, per_page=20)
    assert total == 45
    assert len(users) == 20


def test_list_publications_for_moderation_pagination(monkeypatch):
    def fake_query_db(query, args=(), one=False):
        if 'COUNT(*)' in query:
            return {'total': 3}
        return [{'id': i} for i in range(3)]

    monkeypatch.setattr(admin_model, 'query_db', fake_query_db)

    pubs, total = admin_model.list_publications_for_moderation(filters={'estado': 'Activa'}, page=1, per_page=20)
    assert total == 3
    assert len(pubs) == 3
