"""Descarga la base de datos de la nube (Aiven) a tu MySQL local (XAMPP),
en una base APARTE llamada `coagrix_nube`, para verla en phpMyAdmin.
También genera `exportes/usuarios_AAAA-MM-DD.csv` (se abre con Excel).

No toca tu base local de trabajo (la del .env). Cada vez que lo ejecutas,
`coagrix_nube` se reemplaza con la copia más reciente de la nube.

Uso (desde la carpeta del proyecto, con XAMPP/MySQL encendido):
    .\\venv\\Scripts\\python.exe scripts\\descargar_de_aiven.py

Los datos de Aiven se piden por teclado, o se toman de las variables de
entorno REMOTE_HOST, REMOTE_PORT, REMOTE_USER, REMOTE_PASSWORD, REMOTE_DATABASE.
"""
import csv
import datetime
import getpass
import os
import sys

import mysql.connector

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from config import Config  # noqa: E402

BASE_LOCAL = 'coagrix_nube'
BATCH = 500


def pedir(texto, defecto=''):
    valor = input(f"{texto}{f' [{defecto}]' if defecto else ''}: ").strip()
    return valor or defecto


def main():
    host = os.environ.get('REMOTE_HOST') or pedir("Host de Aiven")
    port = int(os.environ.get('REMOTE_PORT') or pedir("Port"))
    user = os.environ.get('REMOTE_USER') or pedir("User", "avnadmin")
    database = os.environ.get('REMOTE_DATABASE') or pedir("Database name", "defaultdb")
    password = os.environ.get('REMOTE_PASSWORD') or getpass.getpass("Password (no se verá al escribir): ")

    nube = mysql.connector.connect(
        host=host, port=port, user=user, password=password, database=database,
        ssl_disabled=False, connection_timeout=20,
    )
    nc = nube.cursor()
    nc.execute("SET time_zone = '+00:00'")
    # Aiven usa ANSI_QUOTES: sin esto SHOW CREATE TABLE sale con "comillas"
    # dobles, que MariaDB/XAMPP no entiende.
    nc.execute("SET SESSION sql_mode = ''")

    local = mysql.connector.connect(
        host=Config.MYSQL_HOST, port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER, password=Config.MYSQL_PASSWORD,
    )
    lc = local.cursor()
    lc.execute(f"CREATE DATABASE IF NOT EXISTS `{BASE_LOCAL}` "
               "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
    lc.execute(f"USE `{BASE_LOCAL}`")
    lc.execute("SET FOREIGN_KEY_CHECKS = 0")
    lc.execute("SET time_zone = '+00:00'")

    nc.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
    tablas = [fila[0] for fila in nc.fetchall()]
    print(f"Descargando {len(tablas)} tablas a la base local '{BASE_LOCAL}'...")
    for t in tablas:
        nc.execute(f"SHOW CREATE TABLE `{t}`")
        create_sql = nc.fetchone()[1]
        lc.execute(f"DROP TABLE IF EXISTS `{t}`")
        lc.execute(create_sql)

        nc.execute(f"SELECT * FROM `{t}`")
        columnas = ", ".join(f"`{d[0]}`" for d in nc.description)
        marcas = ", ".join(["%s"] * len(nc.description))
        insert = f"INSERT INTO `{t}` ({columnas}) VALUES ({marcas})"
        total = 0
        while True:
            filas = nc.fetchmany(BATCH)
            if not filas:
                break
            lc.executemany(insert, filas)
            total += len(filas)
        local.commit()
        print(f"  OK {t}: {total} filas")
    lc.execute("SET FOREIGN_KEY_CHECKS = 1")

    # Exportar usuarios a CSV (utf-8-sig para que Excel muestre bien las tildes).
    nc.execute(
        "SELECT u.id, u.nombre, u.email, r.nombre AS rol, u.estado "
        "FROM usuarios u JOIN roles r ON r.id = u.rol_id ORDER BY u.id"
    )
    filas = nc.fetchall()
    carpeta = os.path.join(RAIZ, 'exportes')
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"usuarios_{datetime.date.today().isoformat()}.csv")
    with open(ruta, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow([d[0] for d in nc.description])
        w.writerows(filas)

    nc.close()
    nube.close()
    lc.close()
    local.close()
    print(f"\nListo. Abre phpMyAdmin -> base '{BASE_LOCAL}'.")
    print(f"Usuarios en Excel: {ruta}  ({len(filas)} usuarios)")


if __name__ == '__main__':
    main()
