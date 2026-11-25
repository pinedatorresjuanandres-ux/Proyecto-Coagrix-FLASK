"""Sincroniza publicaciones.imagen y archivos.ruta con las imágenes que
existen de verdad en static/uploads/.

Uso: cada vez que la base de datos y la carpeta static/uploads/ quedan
desincronizadas (por ejemplo al copiar el proyecto a otro PC, o al
restaurar la BD desde un dump distinto a las imágenes que hay en
disco), corre este script. Para cada publicación cuya imagen no exista
físicamente en static/uploads/ (o no tenga ninguna asignada), le asigna
una de las imágenes ya presentes en esa carpeta, repartiéndolas entre
las publicaciones rotas. No descarga ni genera nada nuevo, no borra
archivos: solo reutiliza lo que ya está en disco. Es idempotente, se
puede ejecutar las veces que haga falta.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config  # noqa: E402
from database import query_db, execute_db  # noqa: E402


def archivos_disponibles():
    archivos = [
        f for f in os.listdir(Config.UPLOAD_FOLDER)
        if os.path.isfile(os.path.join(Config.UPLOAD_FOLDER, f)) and f != '.gitkeep'
    ]
    archivos.sort()
    return archivos


def main():
    disponibles = archivos_disponibles()
    if not disponibles:
        print(f"No hay ninguna imagen en {Config.UPLOAD_FOLDER}. Nada que sincronizar.")
        return

    publicaciones = query_db("SELECT id, imagen FROM publicaciones") or []

    rotas = []
    for pub in publicaciones:
        imagen = pub['imagen']
        if not imagen:
            rotas.append(pub['id'])
            continue
        filename = imagen.split('/')[-1]
        if not os.path.isfile(os.path.join(Config.UPLOAD_FOLDER, filename)):
            rotas.append(pub['id'])

    if not rotas:
        print("Todas las publicaciones ya apuntan a una imagen que existe en disco. Nada que hacer.")
        return

    print(f"Publicaciones con imagen rota o ausente: {len(rotas)}")
    print(f"Imágenes disponibles en static/uploads/: {len(disponibles)}")

    for i, pub_id in enumerate(rotas):
        filename = disponibles[i % len(disponibles)]
        ruta = f"uploads/{filename}"
        execute_db("UPDATE publicaciones SET imagen = %s WHERE id = %s", (ruta, pub_id))

        existentes = query_db("SELECT id FROM archivos WHERE publicacion_id = %s", (pub_id,)) or []
        if existentes:
            execute_db("UPDATE archivos SET ruta = %s WHERE publicacion_id = %s", (ruta, pub_id))
        else:
            execute_db("INSERT INTO archivos (publicacion_id, ruta) VALUES (%s, %s)", (pub_id, ruta))

        print(f"  publicacion_id={pub_id} -> {ruta}")

    print(
        "\nListo. Este script es idempotente: solo toca publicaciones cuya "
        "imagen no exista ya en disco, así que puedes volver a correrlo "
        "sin riesgo cada vez que muevas el proyecto (con su carpeta "
        "static/uploads/) a otro PC."
    )


if __name__ == '__main__':
    main()
