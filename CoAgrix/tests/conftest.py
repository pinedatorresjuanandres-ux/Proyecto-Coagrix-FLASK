import os
import sys

# Variables de entorno necesarias ANTES de importar config/app, para que la
# app arranque en modo "test" (sin exigir una SECRET_KEY de producción, con
# CSRF desactivado para poder simular formularios sin tener que extraer el
# token de cada página).
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('MYSQL_HOST', 'localhost')
os.environ.setdefault('MYSQL_DATABASE', 'coagrix_test')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,  # los tests de rutas no necesitan probar CSRF en sí
        RATELIMIT_ENABLED=False,  # evita que límites de intentos afecten otros tests
    )
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login_as(client):
    """Helper para simular una sesión ya autenticada.
    Uso: login_as(user_id=1, role_name='Campesino')
    """
    def _login(user_id=1, user_name='Test User', role_id=2, role_name='Campesino'):
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_name'] = user_name
            sess['role_id'] = role_id
            sess['role_name'] = role_name
        return client
    return _login
