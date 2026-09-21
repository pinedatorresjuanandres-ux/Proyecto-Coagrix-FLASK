"""Pruebas del chat (editar, eliminar, responder). Se mockea la capa de
modelos, igual que en test_idor_protection.py: se verifica que las rutas
respeten propiedad, ventana de edición y que nunca filtren contenido eliminado."""
from datetime import datetime

import Controlador.message_controller as chat

ME, OTHER = 1, 2


def _msg(id=10, remitente=ME, destinatario=OTHER, contenido='hola', minutos=1, **extra):
    base = {
        'id': id, 'remitente_id': remitente, 'destinatario_id': destinatario,
        'contenido': contenido, 'fecha': datetime(2026, 9, 21, 10, 0, 0), 'leido': 0,
        'editado_en': None, 'eliminado_para_todos': 0, 'respuesta_a_id': None,
        'minutos': minutos,
    }
    base.update(extra)
    return base


def _setup(monkeypatch, message=None, messages=None):
    monkeypatch.setattr(chat, 'ensure_chat_schema', lambda: None)
    monkeypatch.setattr(chat, 'get_user_by_id',
                        lambda uid: {'id': uid, 'nombre': 'Otro' if uid == OTHER else 'Yo', 'email': 'x@x.co'})
    monkeypatch.setattr(chat, 'get_message', lambda mid: message)
    monkeypatch.setattr(chat, 'get_messages_with_user', lambda a, b: messages or [])
    monkeypatch.setattr(chat, 'get_message_conversations', lambda uid, filters=None: [])
    monkeypatch.setattr(chat, 'mark_conversation_as_read', lambda a, b: None)


def test_deleted_message_never_leaks_content():
    m = _msg(contenido='secreto', eliminado_para_todos=1)
    data = chat.serialize_message(m, ME, 'Otro')
    assert data['eliminado'] is True
    assert data['contenido'] == ''
    assert data['puede_editar'] is False


def test_deleted_reply_preview_hides_original_text():
    m = _msg(respuesta_a_id=5, respuesta_remitente_id=OTHER, respuesta_contenido='texto viejo', respuesta_eliminado=1)
    data = chat.serialize_message(m, ME, 'Otro')
    assert data['respuesta']['contenido'] == ''
    assert data['respuesta']['eliminado'] is True
    assert data['respuesta']['autor'] == 'Otro'


def test_edit_window_flag():
    assert chat.serialize_message(_msg(minutos=5), ME, 'Otro')['puede_editar'] is True
    assert chat.serialize_message(_msg(minutos=15), ME, 'Otro')['puede_editar'] is False
    assert chat.serialize_message(_msg(remitente=OTHER, destinatario=ME, minutos=1), ME, 'Otro')['puede_editar'] is False


def test_edit_own_message(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, message=_msg())
    saved = {}
    monkeypatch.setattr(chat, 'edit_message', lambda mid, texto: saved.update(id=mid, texto=texto) or True)

    resp = client.post('/mensajes/mensaje/10/editar', data={'contenido': '  nuevo texto '})
    assert resp.status_code == 200
    assert saved == {'id': 10, 'texto': 'nuevo texto'}


def test_cannot_edit_someone_elses_message(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, message=_msg(remitente=OTHER, destinatario=ME))
    monkeypatch.setattr(chat, 'edit_message', lambda *a: (_ for _ in ()).throw(AssertionError('no debe editar')))

    resp = client.post('/mensajes/mensaje/10/editar', data={'contenido': 'hack'})
    assert resp.status_code == 403


def test_cannot_edit_after_window(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, message=_msg(minutos=chat.EDIT_WINDOW_MINUTES))
    monkeypatch.setattr(chat, 'edit_message', lambda *a: (_ for _ in ()).throw(AssertionError('no debe editar')))

    resp = client.post('/mensajes/mensaje/10/editar', data={'contenido': 'tarde'})
    assert resp.status_code == 400


def test_cannot_edit_to_empty(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, message=_msg())
    resp = client.post('/mensajes/mensaje/10/editar', data={'contenido': '   '})
    assert resp.status_code == 400


def test_stranger_cannot_touch_message(client, login_as, monkeypatch):
    login_as(user_id=99)
    _setup(monkeypatch, message=_msg())
    for action in ('editar', 'eliminar'):
        resp = client.post(f'/mensajes/mensaje/10/{action}', data={'contenido': 'x', 'modo': 'mi'})
        assert resp.status_code == 404


def test_recipient_can_delete_for_self_but_not_for_everyone(client, login_as, monkeypatch):
    login_as(user_id=OTHER)
    _setup(monkeypatch, message=_msg())  # el mensaje lo escribió ME
    hidden, wiped = [], []
    monkeypatch.setattr(chat, 'delete_message_for_user', lambda m, uid: hidden.append(uid) or True)
    monkeypatch.setattr(chat, 'delete_message_for_everyone', lambda mid: wiped.append(mid) or True)

    assert client.post('/mensajes/mensaje/10/eliminar', data={'modo': 'todos'}).status_code == 403
    assert client.post('/mensajes/mensaje/10/eliminar', data={'modo': 'mi'}).status_code == 200
    assert hidden == [OTHER]
    assert wiped == []


def test_author_deletes_for_everyone(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, message=_msg())
    wiped = []
    monkeypatch.setattr(chat, 'delete_message_for_everyone', lambda mid: wiped.append(mid) or True)

    resp = client.post('/mensajes/mensaje/10/eliminar', data={'modo': 'todos'})
    assert resp.status_code == 200
    assert wiped == [10]


def test_invalid_delete_mode_rejected(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, message=_msg())
    assert client.post('/mensajes/mensaje/10/eliminar', data={'modo': 'otro'}).status_code == 400


def test_send_ignores_reply_to_message_from_another_chat(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    monkeypatch.setattr(chat, 'message_in_conversation', lambda mid, a, b: False)
    sent = {}
    monkeypatch.setattr(chat, 'send_message',
                        lambda a, b, texto, respuesta_a_id=None: sent.update(reply=respuesta_a_id) or 1)

    resp = client.post(f'/mensajes/{OTHER}/enviar', data={'contenido': 'hola', 'respuesta_a_id': '77'})
    assert resp.status_code == 200
    assert sent['reply'] is None


def test_send_rejects_empty_and_too_long(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    assert client.post(f'/mensajes/{OTHER}/enviar', data={'contenido': '  '}).status_code == 400
    too_long = 'x' * (chat.MAX_MESSAGE_LENGTH + 1)
    assert client.post(f'/mensajes/{OTHER}/enviar', data={'contenido': too_long}).status_code == 400


def test_cannot_message_yourself(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    assert client.post(f'/mensajes/{ME}/enviar', data={'contenido': 'hola'}).status_code == 400


def test_clear_only_affects_own_side(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    calls = []
    monkeypatch.setattr(chat, 'clear_conversation', lambda a, b: calls.append((a, b)) or True)

    assert client.post(f'/mensajes/{OTHER}/vaciar').status_code == 200
    assert calls == [(ME, OTHER)]


def test_poll_returns_messages_and_marks_read(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, messages=[_msg(id=1), _msg(id=2, remitente=OTHER, destinatario=ME)])
    read = []
    monkeypatch.setattr(chat, 'mark_conversation_as_read', lambda a, b: read.append((a, b)))

    resp = client.get(f'/mensajes/{OTHER}/lista')
    assert resp.status_code == 200
    body = resp.get_json()
    assert [m['id'] for m in body['messages']] == [1, 2]
    assert [m['mio'] for m in body['messages']] == [True, False]
    assert read == [(OTHER, ME)]


def test_chat_endpoints_require_login(client):
    for path in (f'/mensajes/{OTHER}/lista',):
        assert client.get(path).status_code == 302
    assert client.post('/mensajes/mensaje/10/eliminar', data={'modo': 'mi'}).status_code == 302


def test_conversation_page_renders_with_embedded_data(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch, messages=[_msg(id=1, contenido='</script><b>x</b>')])
    monkeypatch.setattr(chat, 'get_appointments_between', lambda a, b: [])

    resp = client.get(f'/mensajes/{OTHER}')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert 'id="chat-root"' in html and 'js/chat.js' in html
    # el contenido del usuario va escapado dentro del JSON incrustado
    assert '</script><b>x</b>' not in html


# ---- Última cita + historial --------------------------------------------------

def _cita(id, fecha, estado='Pendiente'):
    return {'id': id, 'fecha': fecha, 'hora': '10:00:00', 'estado': estado, 'lugar': 'Plaza',
            'motivo': f'Motivo {id}', 'mensaje': None, 'solicitante_id': OTHER, 'receptor_id': ME,
            'solicitante_nombre': 'Otro'}


def test_split_appointments_latest_is_most_recently_created():
    citas = [_cita(1, '2026-10-01'), _cita(3, '2026-09-25'), _cita(2, '2026-11-01')]
    latest, history = chat.split_appointments(citas)
    assert latest['id'] == 3
    assert [c['id'] for c in history] == [2, 1, 3]  # todas, de la fecha más lejana a la más antigua


def test_split_appointments_empty():
    assert chat.split_appointments([]) == (None, [])


def test_chat_shows_only_latest_and_history_lives_in_modal(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    monkeypatch.setattr(chat, 'get_appointments_between',
                        lambda a, b: [_cita(1, '2026-10-01', 'Aceptada'), _cita(2, '2026-10-05', 'Pendiente')])

    html = client.get(f'/mensajes/{OTHER}').get_data(as_text=True)
    body, modal = html.split('id="history-modal"')
    assert 'Última cita · pendiente' in body and 'Motivo 2' in body
    assert 'Motivo 1' not in body.split('id="chat-box"')[1]  # la anterior ya no está en el chat
    assert 'Motivo 1' in modal and 'Motivo 2' in modal      # el historial las trae todas
    assert 'data-count="2"' in modal and 'data-pending="1"' in modal
    assert '<details' not in html


def test_history_modal_without_appointments_shows_empty_message(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    monkeypatch.setattr(chat, 'get_appointments_between', lambda a, b: [])
    html = client.get(f'/mensajes/{OTHER}').get_data(as_text=True)
    assert 'data-count="0"' in html and 'Aún no hay citas agendadas' in html
    assert 'Última cita' not in html


# ---- Chat del administrador fijado ---------------------------------------------

import Modelo.message as model


def _conv(uid, nombre, no_leidos=0):
    return {'otro_usuario_id': uid, 'nombre': nombre, 'email': f'{nombre}@x.co',
            'ultima_fecha': datetime(2026, 9, 21), 'ultimo_mensaje': 'hola', 'no_leidos': no_leidos}


ADMIN = {'id': 50, 'nombre': 'Admin', 'email': 'admin@x.co'}


def test_admin_chat_is_pinned_even_without_messages(monkeypatch):
    monkeypatch.setattr(model, 'get_pinned_admins', lambda uid: [ADMIN])
    result = model._pin_admin_conversations(ME, [_conv(7, 'Ana')], {})
    assert [c['otro_usuario_id'] for c in result] == [50, 7]
    assert result[0]['fijado'] is True and result[0]['ultimo_mensaje'] is None
    assert not result[1].get('fijado')


def test_existing_admin_conversation_moves_to_top_without_duplicating(monkeypatch):
    monkeypatch.setattr(model, 'get_pinned_admins', lambda uid: [ADMIN])
    convs = [_conv(7, 'Ana'), _conv(50, 'Admin', no_leidos=2), _conv(8, 'Beto')]
    result = model._pin_admin_conversations(ME, convs, {})
    assert [c['otro_usuario_id'] for c in result] == [50, 7, 8]
    assert result[0]['no_leidos'] == 2 and result[0]['fijado'] is True


def test_active_filter_does_not_invent_admin_conversation(monkeypatch):
    monkeypatch.setattr(model, 'get_pinned_admins', lambda uid: [ADMIN])
    assert model._pin_admin_conversations(ME, [_conv(7, 'Ana')], {'estado': 'no_leidos'})[0]['otro_usuario_id'] == 7


def test_nothing_pinned_when_no_admins(monkeypatch):
    monkeypatch.setattr(model, 'get_pinned_admins', lambda uid: [])
    convs = [_conv(7, 'Ana')]
    assert model._pin_admin_conversations(ME, convs, {}) == convs


def test_poll_payload_includes_pinned_flag(client, login_as, monkeypatch):
    login_as(user_id=ME)
    _setup(monkeypatch)
    pinned = _conv(50, 'Admin'); pinned['fijado'] = True
    monkeypatch.setattr(chat, 'get_message_conversations', lambda uid, filters=None: [pinned, _conv(7, 'Ana')])
    body = client.get(f'/mensajes/{OTHER}/lista').get_json()
    assert [c['fijado'] for c in body['conversations']] == [True, False]
