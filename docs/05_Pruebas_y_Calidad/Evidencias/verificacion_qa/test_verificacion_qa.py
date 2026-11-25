"""Verificaciones del Plan de Aseguramiento de Calidad de CoAgrix.

Cada prueba comprueba un criterio de aceptación o una restricción del documento
de requisitos (Especificacion_Requisitos_CoAgrix.docx). La prueba afirma el
comportamiento EXIGIDO: si falla, el criterio queda como «Rechazado» en las
matrices de calidad.

Entorno: cliente de pruebas de Flask con la capa Modelo simulada (no usa un
MySQL real, igual que la suite de tests/). Por eso no mide rendimiento ni
disponibilidad.

Ejecutar desde la raíz del proyecto:
    venv\\Scripts\\python -m pytest docs/05_Pruebas_y_Calidad/Evidencias/verificacion_qa -v
"""
import os
import sys
from datetime import date, timedelta

os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('MYSQL_DATABASE', 'coagrix_test')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, ROOT)

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
import Controlador.auth_controller as auth  # noqa: E402
import Controlador.farmer_controller as farmer  # noqa: E402
import Controlador.product_controller as product  # noqa: E402
import Controlador.appointment_controller as appt  # noqa: E402
import Controlador.account_controller as account  # noqa: E402

UBIC = {'Antioquia': ['Marinilla']}
BASE_FORM = {'nombre': 'Juan Perez', 'email': 'nuevo@example.com', 'telefono': '3101234567',
             'departamento': 'Antioquia', 'municipio': 'Marinilla', 'direccion': ''}


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
    return flask_app.test_client()


def login(client, user_id=1, role_name='Campesino', role_id=2):
    with client.session_transaction() as s:
        s.update(user_id=user_id, user_name='Prueba', role_id=role_id, role_name=role_name)


def mock_registro(monkeypatch, existing=None, created=None):
    created = created if created is not None else {}
    monkeypatch.setattr(auth, 'get_user_by_email', lambda e: existing)
    monkeypatch.setattr(auth, 'create_user', lambda *a: created.setdefault('user', a) and 10)
    monkeypatch.setattr(auth, 'create_location', lambda *a, **k: 5)
    monkeypatch.setattr(auth, 'is_valid_location', lambda d, m: m in UBIC.get(d, []))
    monkeypatch.setattr(auth, 'get_ubicaciones_colombia', lambda: UBIC)
    for f in ('create_farmer_profile', 'create_company_profile', 'create_merchant_profile'):
        monkeypatch.setattr(auth, f, lambda *a, **k: created.setdefault('perfil', a) and True)
    return created


def flashes(client):
    with client.session_transaction() as s:
        return [m for _, m in s.get('_flashes', [])]


# ---------------- RF-1 Registrar usuarios ----------------
def test_CP01_registro_campesino_valido(client, monkeypatch):
    created = mock_registro(monkeypatch)
    r = client.post('/register/campesino', data=dict(BASE_FORM, password='Contrasena10', password_confirm='Contrasena10'))
    assert r.status_code == 302 and 'user' in created


def test_CP02_registro_correo_repetido(client, monkeypatch):
    created = mock_registro(monkeypatch, existing={'id': 3})
    client.post('/register/campesino', data=dict(BASE_FORM, password='Contrasena10', password_confirm='Contrasena10'))
    assert 'user' not in created
    assert 'El correo ya está registrado.' in flashes(client)


def test_CP03_contrasena_menor_a_10_caracteres_se_rechaza(client, monkeypatch):
    """RF-1: «La contraseña debe cumplir mínimo 10 caracteres». Se usa una de 9."""
    created = mock_registro(monkeypatch)
    client.post('/register/campesino', data=dict(BASE_FORM, password='Abcdefgh1', password_confirm='Abcdefgh1'))
    assert 'user' not in created, 'El sistema aceptó una contraseña de 9 caracteres'


# ---------------- RF-19 Registro de empresas ----------------
def test_CP04_registro_empresa_con_nit(client, monkeypatch):
    created = mock_registro(monkeypatch)
    r = client.post('/register/empresa', data=dict(BASE_FORM, nit='900123456-1', sector='Alimentos',
                                                   password='Contrasena10', password_confirm='Contrasena10'))
    assert r.status_code == 302 and 'perfil' in created


def test_CP05_nit_repetido_se_rechaza(client, monkeypatch):
    """RF-19: «La información empresarial no puede repetirse». Se registra un NIT que ya existe con otro correo."""
    created = mock_registro(monkeypatch)
    monkeypatch.setattr('Modelo.user.query_db', lambda *a, **k: {'id': 7})  # el NIT ya existe en empresas
    client.post('/register/empresa', data=dict(BASE_FORM, email='otra@example.com', nit='900123456-1',
                                               password='Contrasena10', password_confirm='Contrasena10'))
    assert 'perfil' not in created, 'El sistema registró una empresa con un NIT ya existente'


# ---------------- RF-3 Inicio de sesión ----------------
def test_CP06_login_credenciales_incorrectas(client, monkeypatch):
    monkeypatch.setattr(auth, 'get_user_by_email', lambda e: None)
    r = client.post('/login', data={'email': 'x@example.com', 'password': 'mala'})
    assert 'Credenciales incorrectas.' in r.get_data(as_text=True)
    with client.session_transaction() as s:
        assert 'user_id' not in s


def test_CP07_login_correcto_abre_panel_del_rol(client, monkeypatch):
    from werkzeug.security import generate_password_hash
    user = {'id': 4, 'nombre': 'Ana', 'rol_id': 3, 'estado': 'Activo', 'password': generate_password_hash('Contrasena10')}
    monkeypatch.setattr(auth, 'get_user_by_email', lambda e: user)
    monkeypatch.setattr(auth, 'get_role_name', lambda rid: 'Empresa')
    r = client.post('/login', data={'email': 'ana@example.com', 'password': 'Contrasena10'})
    assert r.status_code == 302 and '/company/dashboard' in r.headers['Location']


def test_CP08_cuenta_inactiva_no_ingresa(client, monkeypatch):
    from werkzeug.security import generate_password_hash
    user = {'id': 4, 'nombre': 'Ana', 'rol_id': 3, 'estado': 'Inactivo', 'password': generate_password_hash('Contrasena10')}
    monkeypatch.setattr(auth, 'get_user_by_email', lambda e: user)
    client.post('/login', data={'email': 'ana@example.com', 'password': 'Contrasena10'})
    with client.session_transaction() as s:
        assert 'user_id' not in s


# ---------------- RF-4 Coordinación de encuentros ----------------
def _mock_citas(monkeypatch, store):
    monkeypatch.setattr(appt, 'get_user_by_id', lambda uid: {'id': uid})
    monkeypatch.setattr(appt, 'has_schedule_conflict', lambda *a: False)
    monkeypatch.setattr(appt, 'create_appointment', lambda *a: store.setdefault('citas', []).append(a) or True)
    monkeypatch.setattr(appt, 'create_notification', lambda uid, msg: store.setdefault('notif', []).append((uid, msg)))


def test_CP09_cita_con_fecha_de_hoy_se_rechaza(client, monkeypatch):
    store = {}
    _mock_citas(monkeypatch, store)
    login(client)
    client.post('/citas/crear/2', data={'fecha': date.today().isoformat(), 'hora': '10:00', 'motivo': 'Visita'})
    assert 'citas' not in store


def test_CP10_cita_futura_se_crea_y_notifica(client, monkeypatch):
    store = {}
    _mock_citas(monkeypatch, store)
    login(client)
    client.post('/citas/crear/2', data={'fecha': (date.today() + timedelta(days=3)).isoformat(), 'hora': '10:00', 'motivo': 'Visita'})
    assert len(store.get('citas', [])) == 1 and store['notif'][0][0] == 2


# ---------------- RF-6 Gestión de perfil ----------------
def test_CP11_perfil_no_permite_correo_de_otro_usuario(client, monkeypatch):
    saved = {}
    monkeypatch.setattr(account, 'get_user_by_email', lambda e: {'id': 99})
    monkeypatch.setattr(account, 'update_user_profile', lambda *a: saved.setdefault('upd', a))
    login(client, user_id=1)
    client.post('/cuenta/perfil', data={'nombre': 'Juan', 'email': 'ajeno@example.com'})
    assert 'upd' not in saved


# ---------------- RF-9 Gestión de inventario ----------------
def test_CP12_cantidad_negativa_se_rechaza(client, monkeypatch):
    """RF-9: «Las cantidades no pueden ser negativas» (validación en el servidor)."""
    saved = {}
    monkeypatch.setattr(farmer, 'get_farmer_data', lambda uid: {'id': 1})
    monkeypatch.setattr(farmer, 'get_or_create_producto', lambda *a: 1)
    monkeypatch.setattr(farmer, 'get_all_categories', lambda: [])
    monkeypatch.setattr(farmer, 'create_publication', lambda *a, **k: saved.setdefault('pub', a) and 5)
    login(client)
    client.post('/farmer/publicaciones/crear', data={'nombre_producto': 'Papa', 'categoria_id': '1', 'descripcion': 'x',
                                                    'precio_empresa': '1000', 'precio_comerciante': '900',
                                                    'cantidad': '-5', 'unidad': 'kg'})
    assert 'pub' not in saved, 'El servidor guardó una publicación con cantidad -5'


# ---------------- RF-13 Calificación de usuarios ----------------
def test_CP13_calificar_sin_negociacion_se_rechaza(client, monkeypatch):
    """RF-13: «Solo se podrá calificar después de una negociación realizada»."""
    saved = {}
    monkeypatch.setattr(product, 'user_has_reviewed', lambda *a: False)
    monkeypatch.setattr(product, 'create_review', lambda *a: saved.setdefault('review', a))
    login(client, user_id=8, role_name='Empresa', role_id=3)  # usuario sin pedidos
    client.post('/productos/5/resena', data={'calificacion': '5', 'comentario': 'Bien'})
    assert 'review' not in saved, 'Se guardó una calificación sin pedido completado'


# ---------------- RF-17 Eliminación de publicaciones ----------------
def test_CP14_no_se_elimina_publicacion_ajena(client, monkeypatch):
    deleted = {}
    monkeypatch.setattr(farmer, 'get_farmer_data', lambda uid: {'id': 1})
    monkeypatch.setattr(farmer, 'get_publication_by_id', lambda pid: {'id': pid, 'campesino_id': 2, 'imagen': None})
    monkeypatch.setattr(farmer, 'delete_publication', lambda pid: deleted.setdefault('x', pid))
    login(client)
    client.post('/farmer/publicaciones/9/eliminar')
    assert 'x' not in deleted


def test_CP15_error_al_eliminar_no_se_reporta_como_exito(client, monkeypatch):
    """Si la base de datos no elimina la publicación (por ejemplo, porque ya tiene pedidos o
    reseñas asociadas), el sistema no debe decir que se eliminó ni borrar su imagen."""
    images = {}
    monkeypatch.setattr(farmer, 'get_farmer_data', lambda uid: {'id': 1})
    monkeypatch.setattr(farmer, 'get_publication_by_id', lambda pid: {'id': pid, 'campesino_id': 1, 'imagen': 'uploads/a.jpg'})
    monkeypatch.setattr(farmer, 'delete_publication', lambda pid: False)  # execute_db devuelve False
    monkeypatch.setattr(farmer, '_delete_physical_image', lambda ruta: images.setdefault('borrada', ruta))
    login(client)
    client.post('/farmer/publicaciones/9/eliminar')
    assert 'Publicación eliminada correctamente.' not in flashes(client)
    assert 'borrada' not in images


# ---------------- RF-16 Panel administrativo / RNF-6 Seguridad ----------------
def test_CP16_usuario_no_admin_no_entra_al_panel(client):
    login(client, role_name='Campesino')
    r = client.get('/admin/usuarios')
    assert r.status_code in (302, 403) and '/admin/usuarios' not in r.headers.get('Location', '')


def test_CP17_rutas_protegidas_exigen_sesion(client):
    for url in ('/farmer/dashboard', '/company/dashboard', '/merchant/dashboard', '/admin/dashboard', '/carrito/pedidos'):
        r = client.get(url)
        assert r.status_code in (302, 401, 403), url


def test_CP18_formularios_rechazan_peticion_sin_token_csrf(client):
    flask_app.config.update(WTF_CSRF_ENABLED=True)
    try:
        r = client.post('/login', data={'email': 'a@b.co', 'password': 'x'})
        assert r.status_code == 400
    finally:
        flask_app.config.update(WTF_CSRF_ENABLED=False)


def test_CP19_cierre_de_sesion_no_acepta_get(client):
    """Spec 001 (borrador): el cierre de sesión por GET permite que un sitio externo desconecte al usuario."""
    login(client)
    r = client.get('/logout')
    assert r.status_code == 405, 'La sesión se cerró con una petición GET'


def test_CP20_inicio_de_sesion_renueva_la_sesion(client, monkeypatch):
    """Spec 001 (borrador): al iniciar sesión se deben descartar los datos de la sesión anterior."""
    from werkzeug.security import generate_password_hash
    user = {'id': 4, 'nombre': 'Ana', 'rol_id': 3, 'estado': 'Activo', 'password': generate_password_hash('Contrasena10')}
    monkeypatch.setattr(auth, 'get_user_by_email', lambda e: user)
    monkeypatch.setattr(auth, 'get_role_name', lambda rid: 'Empresa')
    with client.session_transaction() as s:
        s['dato_previo'] = 'x'
    client.post('/login', data={'email': 'ana@example.com', 'password': 'Contrasena10'})
    with client.session_transaction() as s:
        assert 'dato_previo' not in s, 'La sesión anterior se conservó tras iniciar sesión'


# ---------------- RF-8 Búsqueda de productos ----------------
def test_CP21_catalogo_filtra_por_categoria_y_ubicacion(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(product, 'get_active_publications', lambda filters, **k: seen.setdefault('f', filters) and ([], 0) or ([], 0))
    monkeypatch.setattr(product, 'get_all_categories', lambda: [])
    monkeypatch.setattr(product, 'query_db', lambda *a, **k: [])
    login(client, role_name='Comerciante', role_id=4)
    client.get('/productos/catalogo?categoria=3&municipio=Neiva&buscar=papa')
    assert seen['f'] == {'categoria': '3', 'municipio': 'Neiva', 'buscar': 'papa'}


# ---------------- RF-10 Notificaciones ----------------
def test_CP22_las_notificaciones_de_citas_se_muestran_al_usuario():
    """RF-10: el usuario debe ver las notificaciones de solicitudes. Se revisa que alguna
    plantilla o controlador lea la tabla «notificaciones»."""
    hits = []
    for folder in ('Vista', 'Controlador', 'Modelo'):
        for dirpath, _, files in os.walk(os.path.join(ROOT, folder)):
            for f in files:
                if f.endswith(('.py', '.html')):
                    txt = open(os.path.join(dirpath, f), encoding='utf-8').read()
                    if 'FROM notificaciones' in txt or 'notificaciones WHERE' in txt:
                        hits.append(f)
    assert hits, 'Ningún módulo consulta la tabla notificaciones: se guardan pero nunca se muestran'
