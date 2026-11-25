"""Copia la base de datos MySQL local (la del .env) a una base remota
(Aiven u otra MySQL en la nube): estructura + datos de todas las tablas.

Uso (desde la carpeta del proyecto):
    .\\venv\\Scripts\\python.exe scripts\\migrar_a_aiven.py            # copia
    .\\venv\\Scripts\\python.exe scripts\\migrar_a_aiven.py --dry-run  # solo muestra qué copiaría

La contraseña remota se pide por teclado (no se guarda en ningún archivo).
ATENCIÓN: borra y vuelve a crear en el destino las tablas que copia.
"""
import getpass
import os
import sys

import mysql.connector

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config  # noqa: E402

BATCH = 500


def conectar_local():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST, port=Config.MYSQL_PORT, user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD, database=Config.MYSQL_DATABASE,
    )


def pedir(texto, defecto=''):
    valor = input(f"{texto}{f' [{defecto}]' if defecto else ''}: ").strip()
    return valor or defecto


def main():
    dry_run = '--dry-run' in sys.argv

    local = conectar_local()
    lc = local.cursor()
    lc.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
    tablas = [fila[0] for fila in lc.fetchall()]
    print(f"Base local '{Config.MYSQL_DATABASE}': {len(tablas)} tablas")
    for t in tablas:
        lc.execute(f"SELECT COUNT(*) FROM `{t}`")
        print(f"  - {t}: {lc.fetchone()[0]} filas")

    if dry_run:
        print("\n--dry-run: no se copió nada.")
        return

    print("\nDatos de la base REMOTA (cópialos de 'Connection information' en Aiven):")
    # También se pueden pasar por variables de entorno REMOTE_HOST, etc.
    host = os.environ.get('REMOTE_HOST') or pedir("Host")
    port = int(os.environ.get('REMOTE_PORT') or pedir("Port"))
    user = os.environ.get('REMOTE_USER') or pedir("User", "avnadmin")
    database = os.environ.get('REMOTE_DATABASE') or pedir("Database name", "defaultdb")
    password = os.environ.get('REMOTE_PASSWORD') or getpass.getpass("Password (no se verá al escribir): ")

    remoto = mysql.connector.connect(
        host=host, port=port, user=user, password=password, database=database,
        ssl_disabled=False, connection_timeout=20,
    )
    rc = remoto.cursor()
    rc.execute("SET FOREIGN_KEY_CHECKS = 0")
    rc.execute("SET time_zone = '+00:00'")
    lc.execute("SET time_zone = '+00:00'")
    try:
        rc.execute("SET SESSION sql_require_primary_key = 0")
    except mysql.connector.Error:
        pass  # Las tablas se crean con su llave primaria, así que no es necesario.

    for t in tablas:
        lc.execute(f"SHOW CREATE TABLE `{t}`")
        create_sql = lc.fetchone()[1]
        rc.execute(f"DROP TABLE IF EXISTS `{t}`")
        rc.execute(create_sql)

        lc.execute(f"SELECT * FROM `{t}`")
        columnas = ", ".join(f"`{d[0]}`" for d in lc.description)
        marcas = ", ".join(["%s"] * len(lc.description))
        insert = f"INSERT INTO `{t}` ({columnas}) VALUES ({marcas})"
        total = 0
        while True:
            filas = lc.fetchmany(BATCH)
            if not filas:
                break
            rc.executemany(insert, filas)
            total += len(filas)
        remoto.commit()
        print(f"  OK {t}: {total} filas")

    rc.execute("SET FOREIGN_KEY_CHECKS = 1")
    remoto.commit()
    rc.close()
    remoto.close()
    lc.close()
    local.close()
    print("\nListo: la base quedó copiada en la nube.")


if __name__ == '__main__':
    main()
