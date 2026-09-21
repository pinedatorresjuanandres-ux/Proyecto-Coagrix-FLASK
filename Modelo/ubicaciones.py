from database import query_db


def get_ubicaciones_colombia():
    """Devuelve {departamento: [municipios]} leído de las tablas
    `departamentos` y `municipios` (se cargan con sql/ubicaciones_colombia.sql),
    ordenado alfabéticamente. Alimenta los desplegables del registro."""
    rows = query_db("""
        SELECT d.nombre AS departamento, m.nombre AS municipio
        FROM departamentos d
        JOIN municipios m ON m.departamento_id = d.id
        ORDER BY d.nombre, m.nombre
    """) or []
    ubicaciones = {}
    for row in rows:
        ubicaciones.setdefault(row['departamento'], []).append(row['municipio'])
    return ubicaciones


def is_valid_location(departamento, municipio):
    """True si el municipio pertenece al departamento indicado. La
    comparación es exacta (sin ignorar mayúsculas ni tildes) para guardar
    siempre el nombre oficial."""
    row = query_db("""
        SELECT 1
        FROM municipios m
        JOIN departamentos d ON d.id = m.departamento_id
        WHERE d.nombre = %s COLLATE utf8mb4_bin AND m.nombre = %s COLLATE utf8mb4_bin
        LIMIT 1
    """, (departamento, municipio), one=True)
    return row is not None
