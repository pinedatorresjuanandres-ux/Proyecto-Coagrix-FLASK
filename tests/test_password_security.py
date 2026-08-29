"""Pruebas de la lógica de contraseñas: que se guarden con hash y que las
cuentas antiguas en texto plano se puedan seguir usando y queden
re-hasheadas automáticamente tras un login exitoso."""
from werkzeug.security import generate_password_hash

from models.user import verify_password, upgrade_password_if_plaintext


def test_verify_password_with_correct_hash():
    hashed = generate_password_hash('mi_clave_123')
    assert verify_password(hashed, 'mi_clave_123') is True


def test_verify_password_with_wrong_password():
    hashed = generate_password_hash('mi_clave_123')
    assert verify_password(hashed, 'otra_clave') is False


def test_verify_password_supports_legacy_plaintext():
    # Cuentas creadas antes del cambio a hashing pueden haber quedado con
    # la contraseña guardada tal cual; deben poder seguir autenticándose.
    assert verify_password('clave_en_texto_plano', 'clave_en_texto_plano') is True


def test_upgrade_password_if_plaintext_rehashes(monkeypatch):
    calls = {}

    def fake_execute_db(query, args):
        calls['query'] = query
        calls['args'] = args
        return True

    monkeypatch.setattr('models.user.execute_db', fake_execute_db)

    upgrade_password_if_plaintext(user_id=1, stored_password='clave123', plain_password='clave123')

    assert calls, "Se esperaba que se ejecutara un UPDATE para re-hashear la contraseña"
    assert calls['args'][1] == 1
    # La nueva contraseña guardada ya no debe ser el texto plano original.
    assert calls['args'][0] != 'clave123'


def test_upgrade_password_if_plaintext_noop_when_already_hashed(monkeypatch):
    calls = {}

    def fake_execute_db(query, args):
        calls['called'] = True

    monkeypatch.setattr('models.user.execute_db', fake_execute_db)

    hashed = generate_password_hash('clave123')
    upgrade_password_if_plaintext(user_id=1, stored_password=hashed, plain_password='clave123')

    assert 'called' not in calls, "No debe re-escribir una contraseña que ya estaba hasheada"
