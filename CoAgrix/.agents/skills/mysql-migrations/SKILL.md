---
name: mysql-migrations
description: Úsala siempre que cambies el esquema de la base de datos, escribas SQL nuevo, añadas funciones en Modelo/ o crees archivos en sql/ en CoAgrix.
---
# Base de datos y migraciones en CoAgrix
## Acceso a datos
- Todo el SQL vive en `Modelo/`. Los controladores nunca lo contienen.
- Usa `query_db(sql, args, one=False)` para leer y `execute_db(sql, args)` para escribir.
- Cuidado: `query_db` devuelve `None` cuando falla Y una lista vacía o `None` cuando no hay
  datos (con `one=True`). Trata `None` como "posible error" y no como "no existe" cuando importe.
- `execute_db` devuelve el `lastrowid`, `True` o `False` si falló.
## Migraciones
- Un archivo por cambio en `sql/`, con nombre `migracion_<tema>.sql`.
- Deben ser **idempotentes** (`CREATE TABLE IF NOT EXISTS`, comprobar la columna antes del
  `ALTER`) y **aditivas**: no borrar columnas, tablas ni datos.
- Documenta arriba del archivo qué hace y en qué orden se aplica respecto a las demás.
- Cualquier cambio de esquema necesita aprobación explícita en la spec.
## Reglas
- Nombres de tablas y columnas en español, en minúsculas, como las existentes.
- Fechas en columnas DATETIME; ver `colombia-locale` para la zona horaria.
- Nunca ejecutes SQL destructivo contra datos reales sin copia de seguridad y spec aprobada.
