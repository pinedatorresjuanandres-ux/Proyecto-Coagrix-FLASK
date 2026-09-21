"""Pruebas de "Olvidé mi contraseña" y de cambiar contraseña estando
logueado. Base de datos y correo simulados: se verifica la lógica de las
rutas, la seguridad del token y la transacción de cambio."""
from types import SimpleNamespace

import pytest

import Controlador.auth_controller as auth
import Controlador.account_controller as account
import Modelo.password_reset as pr
from extensions import limiter
from werkzeug.security import generate_password_hash


class _SyncThread:
    """Ejecuta el envío en el mismo hilo para poder comprobarlo."""
    def __init__(self, target, args=(), daemon=None):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    """Cada prueba parte con el contador de intentos en cero."""
    limiter.reset()


USER = {'id': 4, 'nombre': 'Ana', 'email': 'ana@example.com'}


def _setup_forgot(monkeypatch, user, recent=False):
    sent, created = [], []
    monkeypatch.setattr(auth, 'get_user_by_email', lambda e: user if user and e == user['email'] else None)
    monkeypatch.setattr(auth, 'recent_reset_exists', lambda uid: recent)
    monkeypatch.setattr(auth, 'create_reset_token', lambda uid: created.append(uid) or 'TOKEN123')
    monkeypatch.setattr(auth, 'send_email', lambda to, subject, body: sent.append((to, body)))
    # Solo dentro del controlador (no el threading global, que usa el limitador).
    monkeypatch.setattr(auth, 'threading', SimpleNamespace(Thread=_SyncThread))
    return sent, created


def test_olvide_envia_enlace_si_el_correo_existe(client, monkeypatch):
    sent, created = _setup_forgot(monkeypatch, USER)
    resp = client.post('/olvide-contrasena', data={'email': 'ANA@example.com '})
    assert resp.status_code == 302
    assert created == [4]
    assert sent[0][0] == 'ana@example.com'
    assert '/restablecer/TOKEN123' in sent[0][1]


def test_olvide_responde_igual_si_el_correo_no_existe(client, monkeypatch):
    sent, created = _setup_forgot(monkeypatch, USER)
    resp_ok = client.post('/olvide-contrasena', data={'email': 'ana@example.com'}, follow_redirects=True)
    resp_no = client.post('/olvide-contrasena', data={'email': 'nadie@example.com'}, follow_redirects=True)
    # No se envía nada al correo inexistente y el mensaje mostrado es idéntico.
    assert len(sent) == 1
    msg = 'Si el correo está registrado'
    assert msg in resp_ok.get_data(as_text=True) and msg in resp_no.get_data(as_text=True)


def test_olvide_no_reenvia_si_hubo_solicitud_reciente(client, monkeypatch):
    sent, created = _setup_forgot(monkeypatch, USER, recent=True)
    client.post('/olvide-contrasena', data={'email': 'ana@example.com'})
    assert sent == [] and created == []


def test_restablecer_rechaza_token_invalido(client, monkeypatch):
    monkeypatch.setattr(auth, 'is_reset_token_valid', lambda t: False)
    for method in (client.get, client.post):
        resp = method('/restablecer/malo')
        assert resp.status_code == 302 and '/olvide-contrasena' in resp.headers['Location']


def test_restablecer_valida_la_contrasena_nueva(client, monkeypatch):
    monkeypatch.setattr(auth, 'is_reset_token_valid', lambda t: True)
    called = []
    monkeypatch.setattr(auth, 'consume_reset_token', lambda t, p: called.append(p) or True)
    client.post('/restablecer/ok', data={'password': 'corta', 'password_confirm': 'corta'})
    client.post('/restablecer/ok', data={'password': 'Abcdefg1', 'password_confirm': 'Otra1234'})
    assert called == []


def test_restablecer_cambia_la_contrasena(client, monkeypatch):
    monkeypatch.setattr(auth, 'is_reset_token_valid', lambda t: True)
    called = []
    monkeypatch.setattr(auth, 'consume_reset_token', lambda t, p: called.append((t, p)) or 3)
    resp = client.post('/restablecer/ok', data={'password': 'Abcdefg1', 'password_confirm': 'Abcdefg1'})
    assert called == [('ok', 'Abcdefg1')]
    # Al terminar va al login único.
    assert resp.status_code == 302 and resp.headers['Location'].endswith('/login')


def test_restablecer_muestra_mensaje_de_exito_en_el_login(client, monkeypatch):
    monkeypatch.setattr(auth, 'is_reset_token_valid', lambda t: True)
    monkeypatch.setattr(auth, 'consume_reset_token', lambda t, p: 4)
    resp = client.post('/restablecer/ok', data={'password': 'Abcdefg1', 'password_confirm': 'Abcdefg1'},
                       follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'Contraseña actualizada' in html and 'Iniciar Sesión' in html


# --- Modelo: token y transacción -------------------------------------------------

class _Cur:
    def __init__(self, row):
        self.row, self.executed = row, []

    def execute(self, sql, params=()):
        self.executed.append((' '.join(sql.split()), params))

    def fetchone(self):
        return self.row

    def close(self):
        pass


class _Conn:
    def __init__(self, cur):
        self.cur, self.commits, self.rollbacks = cur, 0, 0

    def cursor(self, dictionary=False):
        return self.cur

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        pass


def test_solo_se_guarda_el_hash_del_token(monkeypatch):
    saved = {}
    monkeypatch.setattr(pr, 'execute_db', lambda q, args: saved.update(args=args) or 1)
    token = pr.create_reset_token(4)
    assert token and token not in saved['args']
    assert saved['args'][1] == pr._hash_token(token) and len(saved['args'][1]) == 64


def test_consumir_token_cambia_password_e_invalida_los_demas(monkeypatch):
    cur = _Cur({'usuario_id': 4, 'rol_id': 3})
    conn = _Conn(cur)
    monkeypatch.setattr(pr, 'get_db_connection', lambda: conn)
    assert pr.consume_reset_token('tok', 'Abcdefg1') == 3  # devuelve el rol
    sqls = [s for s, _ in cur.executed]
    assert 'FOR UPDATE' in sqls[0] and 'usado_en IS NULL' in sqls[0] and 'expira_en > NOW()' in sqls[0]
    new_hash = next(p[0] for s, p in cur.executed if s.startswith('UPDATE usuarios'))
    assert new_hash != 'Abcdefg1' and new_hash.split(':')[0] in ('scrypt', 'pbkdf2')
    assert any(s.startswith('UPDATE password_resets SET usado_en') for s in sqls)
    assert conn.commits == 1 and conn.rollbacks == 0


def test_consumir_token_invalido_no_toca_nada(monkeypatch):
    cur = _Cur(None)
    conn = _Conn(cur)
    monkeypatch.setattr(pr, 'get_db_connection', lambda: conn)
    assert pr.consume_reset_token('tok', 'Abcdefg1') is None
    assert len(cur.executed) == 1 and conn.commits == 0 and conn.rollbacks == 1


# --- Cambiar contraseña logueado -------------------------------------------------

def _setup_change(monkeypatch):
    user = {'id': 7, 'password': generate_password_hash('Actual123')}
    monkeypatch.setattr(account, 'get_user_by_id', lambda uid: user)
    changed = []
    monkeypatch.setattr(account, 'update_user_password', lambda uid, p: changed.append((uid, p)))
    return changed


def test_cambiar_contrasena_requiere_login(client):
    resp = client.get('/cuenta/cambiar-contrasena')
    assert resp.status_code == 302 and '/login' in resp.headers['Location']


def test_cambiar_contrasena_exige_la_actual(client, login_as, monkeypatch):
    login_as(user_id=7, role_name='Empresa', role_id=3)
    changed = _setup_change(monkeypatch)
    client.post('/cuenta/cambiar-contrasena',
                data={'password_actual': 'Mala1234', 'password': 'Nueva1234', 'password_confirm': 'Nueva1234'})
    assert changed == []


def test_cambiar_contrasena_ok(client, login_as, monkeypatch):
    login_as(user_id=7, role_name='Empresa', role_id=3)
    changed = _setup_change(monkeypatch)
    resp = client.post('/cuenta/cambiar-contrasena',
                       data={'password_actual': 'Actual123', 'password': 'Nueva1234', 'password_confirm': 'Nueva1234'})
    assert resp.status_code == 302 and changed == [(7, 'Nueva1234')]


def test_cambiar_contrasena_valida_reglas_y_que_sea_distinta(client, login_as, monkeypatch):
    login_as(user_id=7, role_name='Empresa', role_id=3)
    changed = _setup_change(monkeypatch)
    for nueva, confirm in (('Actual123', 'Actual123'), ('corta', 'corta'), ('Nueva1234', 'Otra12345')):
        client.post('/cuenta/cambiar-contrasena',
                    data={'password_actual': 'Actual123', 'password': nueva, 'password_confirm': confirm})
    assert changed == []


def test_paginas_se_muestran(client):
    assert client.get('/olvide-contrasena').status_code == 200
    assert '/olvide-contrasena' in client.get('/login').get_data(as_text=True)
