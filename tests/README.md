# Tests

Esta suite usa `pytest` y el test client de Flask. No requiere un MySQL
real corriendo: la capa de modelos (`models/*.py`) se mockea con
`monkeypatch` en cada test, reemplazando `query_db`/`execute_db` por
funciones falsas que devuelven datos de ejemplo.

## Qué cubre

- **`test_idor_protection.py`**: que un campesino no pueda ver/aceptar/
  rechazar/completar el pedido de otro campesino, y que un comprador no
  pueda ver el pedido de otro comprador, cambiando el id en la URL.
- **`test_password_security.py`**: que las contraseñas se verifiquen por
  hash, que las cuentas antiguas en texto plano sigan pudiendo entrar, y
  que se re-hasheen automáticamente tras un login exitoso.
- **`test_image_upload_validation.py`**: que la subida de imágenes valide
  el contenido real del archivo (no solo la extensión), el tamaño máximo,
  y que se guarde correctamente una imagen válida.
- **`test_pagination.py`**: que la paginación agregada al catálogo y a los
  listados de administración calcule bien el total de páginas y el
  LIMIT/OFFSET.
- **`test_error_pages.py`**: que las páginas de error personalizadas
  (404, redirecciones de rutas protegidas) respondan con el código
  correcto.

## Qué NO cubre (limitaciones conocidas)

- No hay pruebas de integración contra una base de datos MySQL real; las
  consultas SQL en sí (sintaxis, nombres de columnas reales) no se
  validan automáticamente. Si cambias el esquema, corre la aplicación
  manualmente contra una base de datos de prueba además de estos tests.
- No se prueba el comportamiento exacto del rate limiting (Flask-Limiter)
  bajo carga concurrente, solo que está conectado a las rutas.
- No hay pruebas end-to-end de UI/JavaScript.

## Cómo correrlos

```bash
pip install -r requirements.txt
pytest
```
