---
name: flask-pytest
description: Úsala siempre que escribas, modifiques o revises tests en CoAgrix, o cuando implementes una ruta, modelo o validación nueva que necesite pruebas con pytest.
---
# Tests con pytest en CoAgrix
Los tests no usan MySQL: se mockea la capa de modelos con `monkeypatch`.
## Piezas que ya existen (`tests/conftest.py`)
- `client`: test client de Flask, con CSRF y rate limiting desactivados solo para tests.
- `login_as(user_id, user_name, role_id, role_name)`: simula una sesión autenticada.
  Ejemplo: `login_as(user_id=1, role_name='Campesino')`.
## Patrón
- Mockea en el módulo del **controlador** que usa la función, no en el modelo:
  `monkeypatch.setattr(farmer_routes, 'get_farmer_data', lambda uid: {'id': 99})`.
- Prueba siempre el caso feliz y el caso de rechazo (403, redirección, mensaje de error).
- Para verificar que algo se llamó, guarda el hecho en un `dict` y compruébalo al final.
## Qué probar en cada ruta
- Sin sesión → redirige a login. Rol equivocado → bloqueado.
- Recurso ajeno (otro `id` en la URL) → 403 (ver `flask-security`).
- Entrada inválida → mensaje en español y nada se guarda.
- Rutas POST: que un GET no ejecute la acción (405).
## Reglas
- Un test = un comportamiento. Nombres descriptivos: `test_farmer_cannot_view_foreign_order`.
- Nunca desactives CSRF ni el limitador en el código de la app para que pase un test.
- Corre `pytest` completo antes de dar una tarea por terminada.
